"""Client/Server communication protocol.

This module implements a base class for the server/client communication
protocol based on :py:mod:`asyncio`.

laneya is a network based multiplayer game with a central server and multiple
clients that connect to that server.  To avoid cheating, all game logic happens
on the server while all presentation logic happens on the client.  So to
perform any action the client must always send a request to the server.  The
server then performs the following steps:

1.  Check whether the request is *valid*, i.e. all necessary field exist and
    have the right type.  If it is not, send an error response and stop.

2.  Check whether the request is *legal* within the rules of the game.  If it
    is not, send an error response and stop.

3.  Perform the action, e.g. decide whether some action succeeds based on a
    random number.

4.  Broadcast the result of the action to all connected clients.

5.  Send a success response.


Both client and server can initiate messages.  There are three types of
messages:

Request
    The client requests an action from the server.

Response
    A request is always followed by an associated response with status
    "success", "invalid", "illegal" or "internal".

Update
    A server initiated message without response.


.. Note::

    Actions should be as simple as possible to keep the protocol robust.  Some
    things you might think about:

    -   An action should be *idempotent*:  Sending a message twice should have
        the same effect as sending it only one time.  This way it can simply be
        resend if a response has not been received within a specified timeout.

    -   An action should not depend on being send in the right order.  The
        server should however provide a way to send multiple actions in one
        request that are processed in order.

    -   The protocol should be *stateless*.  For example, the client should
        send its userID with every request instead of having the server store
        it with the connection.

.. Note::

    This module implements only the basic structure described above.  The
    actual actions need to be defined and implemented on top of this.

"""


import json
import logging

import trollius as asyncio

from . import promise as q
from . import actions

logger = logging.getLogger('laneya')
logger.addHandler(logging.StreamHandler())
logging.getLogger('trollius').addHandler(logging.StreamHandler())

key = 0


class InvalidError(Exception):
    """The message is not valid, e.g. fields are missing."""
    pass


class IllegalError(Exception):
    """The requested action does not comply with the rules."""
    pass


def generate_key():
    global key
    key += 1
    return key


class LoopingCall(object):
    def __init__(self, loop, fn, *args, **kwargs):
        self.loop = loop
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.running = False
        self.interval = None

    def start(self, interval, now=True):
        self.interval = interval
        self.running = True

        if now:
            self._wrapped()
        else:
            self.loop.call_later(self.interval, self._wrapped)

    def stop(self):
        self.running = False

    def _wrapped(self):
        if self.running:
            self.loop.call_later(self.interval, self._wrapped)
            self.fn(*self.args, **self.kwargs)


class NetstringReceiver(asyncio.Protocol):
    """ protocol that sends and receives netstrings.

    See http://cr.yp.to/proto/netstrings.txt for the specification of
    netstrings.

    """
    def __init__(self):
        self.__buffer = ''
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def string_received(self, data):
        raise NotImplementedError

    def data_received(self, data):
        # FIXME: invalid data should not crash the server
        self.__buffer += data

        while ':' in self.__buffer:
            length, remainder = self.__buffer.split(':', 1)
            length = int(length)

            if len(remainder) > length:
                assert remainder[length] == ','
                s = remainder[:length]
                self.__buffer = self.__buffer[len('%i:%s,' % (length, s)):]
                self.string_received(s)
            else:
                break

    def send_string(self, data):
        self.transport.write('%i:%s,' % (len(data), data))


class JSONProtocol(NetstringReceiver):
    """Send and receive JSON objects."""

    def json_received(self, data):
        raise NotImplementedError

    def string_received(self, s):
        return self.json_received(json.loads(s))

    def send_json(self, data):
        return self.send_string(json.dumps(data))


class BaseProtocol(JSONProtocol):

    def validate_message(self, message, expected_keys):
        if sorted(message.keys()) != expected_keys:
            logger.error('Invalid message: %s' % message)
            raise InvalidError

    def validate_action(self, action, data):
        try:
            fn = getattr(actions, action)
            fn(**data)
        except:
            logger.error('Invalid action: %s %s' % (action, data))
            raise InvalidError


class ServerProtocol(BaseProtocol):
    """Default implementation of the server protocol."""

    def __init__(self, factory):
        super(ServerProtocol, self).__init__()
        self.factory = factory

    def connection_made(self, transport):
        super(ServerProtocol, self).connection_made(transport)
        self.factory.connections.append(self)

    def connection_lost(self, reason):
        self.factory.connections.remove(self)

    def _request_received(self, key, user, action, **data):
        try:
            response = self.factory.request_received(user, action, **data)
        except InvalidError as err:
            return self._send_response(key, 'invalid', message=str(err))
        except IllegalError as err:
            return self._send_response(key, 'illegal', message=str(err))
        except Exception as err:
            logger.error(err)
            return self._send_response(key, 'internal', message=str(err))

        if response is None:
            response = {}

        return self._send_response(key, 'success', **response)

    def json_received(self, message):
        if message['type'] == 'request':
            self.validate_message(
                message, ['action', 'data', 'key', 'type', 'user'])
            self.validate_action(message['action'], message['data'])
            self._request_received(
                message['key'],
                message['user'],
                message['action'],
                **message['data'])
        else:
            logger.error('Message type not known: %s' % message['type'])

    def _send_response(self, key, status, **kwargs):
        data = {
            'type': 'response',
            'key': key,
            'status': status,
            'data': kwargs,
        }
        self.send_json(data)

    def _send_update(self, action, **kwargs):
        data = {
            'type': 'update',
            'action': action,
            'data': kwargs,
        }
        self.send_json(data)


class ServerProtocolFactory(object):
    """Factory for :py:class:`ServerProtocol`."""

    def __init__(self):
        self.connections = []

    def build_protocol(self):
        return ServerProtocol(self)

    def request_received(self, user, action, **kwargs):
        """Overwrite this on the server implementation."""
        raise NotImplementedError

    def broadcast_update(self, action, **kwargs):
        """Broadcast an update to all connected clients."""

        for connection in self.connections:
            connection._send_update(action, **kwargs)


class ClientProtocol(BaseProtocol):
    """Default implementation of the client protocol."""

    def __init__(self, factory):
        super(ClientProtocol, self).__init__()
        self.factory = factory
        self._response_promises = {}

    def connection_made(self, transport):
        super(ClientProtocol, self).connection_made(transport)
        self.factory.connections.append(self)
        self.factory.connection_made()

    def connection_lost(self, reason):
        self.factory.connections.remove(self)

    def json_received(self, message):
        if message['type'] == 'response':
            self.validate_message(message, ['data', 'key', 'status', 'type'])
            key = message['key']
            if key in self._response_promises:
                response = {
                    'status': message['status'],
                    'data': message['data'],
                }
                promise = self._response_promises.pop(key)
                if message['status'] == 'success':
                    promise.resolve(response)
                else:
                    promise.reject(response)

        elif message['type'] == 'update':
            self.validate_message(message, ['action', 'data', 'type'])
            self.validate_action(message['action'], message['data'])
            self.update_received(message['action'], **message['data'])

        else:
            logger.error('Message type not known: %s' % message['type'])

    def update_received(self, action, **kwargs):
        self.factory.update_received(action, **kwargs)

    def _timeout(self, promise, key):
        try:
            promise.reject('timeout')
            del self._response_promises[key]
        except KeyError:
            pass

    def send_request(self, action, **kwargs):
        data = {
            'type': 'request',
            'key': generate_key(),
            'user': self.factory.user,
            'action': action,
            'data': kwargs,
        }
        self.send_json(data)

        promise = q.Promise()
        self._response_promises[data['key']] = promise
        self.factory.loop.call_later(2, self._timeout, promise, data['key'])
        return promise


class ClientProtocolFactory(object):
    """Factory for :py:class:`ClientProtocol`.

    We assume that this factory has only one active connection.
    """

    def __init__(self, loop):
        self.loop = loop
        self.connections = []

    def build_protocol(self):
        return ClientProtocol(self)

    def setup(self, user):
        """Setup the user for all connections."""
        self.user = user

    def send_request(self, action, **kwargs):
        """Send a request and get a promise yielding the response."""
        return self.connections[-1].send_request(action, **kwargs)

    def update_received(self, action, **kwargs):
        """Overwrite this on the client implementation."""
        raise NotImplementedError

    def connection_made(self):
        """Overwrite this on the client implementation."""
        pass


__all__ = [
    'InvalidError',
    'IllegalError',
    'ServerProtocol',
    'ServerProtocolFactory',
    'ClientProtocol',
    'ClientProtocolFactory',
]
