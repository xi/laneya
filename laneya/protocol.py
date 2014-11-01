"""Client/Server communication protocol.

This module implements a base class for the server/client communication
protocol based on :py:mod:`twisted`.

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

from twisted.python import log
from twisted.protocols.basic import NetstringReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor

import deferred as q
import actions


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


class JSONProtocol(NetstringReceiver):
    """Send and receive JSON objects."""

    def jsonReceived(self, data):
        raise NotImplementedError

    def stringReceived(self, s):
        return self.jsonReceived(json.loads(s))

    def sendJSON(self, data):
        return self.sendString(json.dumps(data))


class BaseProtocol(JSONProtocol):

    def validate_message(self, message, expected_keys):
        if sorted(message.keys()) != expected_keys:
            log.err('Invalid message: %s' % message)
            raise InvalidError

    def validate_action(self, action, data):
        try:
            fn = getattr(actions, action)
            fn(**data)
        except:
            log.err('Invalid action: %s %s' % (action, data))
            raise InvalidError


class ServerProtocol(BaseProtocol):
    """Default implementation of the server protocol."""

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.connections.append(self)

    def connectionLost(self, reason):
        self.factory.connections.remove(self)

    def _requestReceived(self, key, user, action, **data):
        try:
            response = self.factory.requestReceived(user, action, **data)
        except InvalidError as err:
            return self._sendResponse(key, 'invalid', message=str(err))
        except IllegalError as err:
            return self._sendResponse(key, 'illegal', message=str(err))
        except Exception as err:
            log.err(err)
            return self._sendResponse(key, 'internal', message=str(err))

        if response is None:
            response = {}

        return self._sendResponse(key, 'success', **response)

    def jsonReceived(self, message):
        if message['type'] == 'request':
            self.validate_message(
                message, ['action', 'data', 'key', 'type', 'user'])
            self.validate_action(message['action'], message['data'])
            self._requestReceived(
                message['key'],
                message['user'],
                message['action'],
                **message['data'])
        else:
            log.err('Message type not known: %s' % message['type'])

    def _sendResponse(self, key, status, **kwargs):
        data = {
            'type': 'response',
            'key': key,
            'status': status,
            'data': kwargs,
        }
        self.sendJSON(data)

    def _sendUpdate(self, action, **kwargs):
        data = {
            'type': 'update',
            'action': action,
            'data': kwargs,
        }
        self.sendJSON(data)


class ServerProtocolFactory(Factory):
    """Factory for :py:class:`ServerProtocol`."""

    def __init__(self):
        self.connections = []

    def buildProtocol(self, addr):
        return ServerProtocol(self)

    def requestReceived(self, user, action, **kwargs):
        """Overwrite this on the server implementation."""
        raise NotImplementedError

    def broadcastUpdate(self, action, **kwargs):
        """Broadcast an update to all connected clients."""

        for connection in self.connections:
            connection._sendUpdate(action, **kwargs)


class ClientProtocol(BaseProtocol):
    """Default implementation of the client protocol."""

    def __init__(self, factory):
        self.factory = factory
        self._responseDeferreds = {}

    def connectionMade(self):
        self.factory.connections.append(self)
        self.factory.connectionMade()

    def connectionLost(self, reason):
        self.factory.connections.remove(self)

    def jsonReceived(self, message):
        if message['type'] == 'response':
            self.validate_message(message, ['data', 'key', 'status', 'type'])
            key = message['key']
            if key in self._responseDeferreds:
                response = {
                    'status': message['status'],
                    'data': message['data'],
                }
                d = self._responseDeferreds.pop(key)
                if message['status'] == 'success':
                    d.resolve(response)
                else:
                    d.reject(response)

        elif message['type'] == 'update':
            self.validate_message(message, ['action', 'data', 'type'])
            self.validate_action(message['action'], message['data'])
            self.updateReceived(message['action'], **message['data'])

        else:
            log.err('Message type not known: %s' % message['type'])

    def updateReceived(self, action, **kwargs):
        self.factory.updateReceived(action, **kwargs)

    def _timeout(self, d, key):
        try:
            d.reject('timeout', silent=True)
            del self._responseDeferreds[key]
        except KeyError:
            pass

    def sendRequest(self, action, **kwargs):
        data = {
            'type': 'request',
            'key': generate_key(),
            'user': self.factory.user,
            'action': action,
            'data': kwargs,
        }
        self.sendJSON(data)

        d = q.Deferred()
        self._responseDeferreds[data['key']] = d
        reactor.callLater(2, lambda: self._timeout(d, data['key']))
        return d.promise


class ClientProtocolFactory(Factory):
    """Factory for :py:class:`ClientProtocol`.

    We assume that this factory has only one active connection.
    """

    def __init__(self):
        self.connections = []

    def buildProtocol(self, addr):
        return ClientProtocol(self)

    def setup(self, user):
        """Setup the user for all connections."""
        self.user = user

    def sendRequest(self, action, **kwargs):
        """Send a request and get a promise yielding the response."""
        return self.connections[-1].sendRequest(action, **kwargs)

    def updateReceived(self, action, **kwargs):
        """Overwrite this on the client implementation."""
        raise NotImplementedError

    def connectionMade(self):
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
