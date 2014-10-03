import json

from twisted.python import log
from twisted.protocols.basic import NetstringReceiver

import deferred as q


key = 0


class InvalidError(Exception):
    pass


class IllegalError(Exception):
    pass


def generate_key():
    global key
    key += 1
    return key


class JSONProtocol(NetstringReceiver):
    def jsonReceived(self, data):
        raise NotImplementedError

    def stringReceived(self, s):
        return self.jsonReceived(json.loads(s))

    def sendJSON(self, data):
        return self.sendString(json.dumps(data))


class Protocol(JSONProtocol):
    def __init__(self):
        self._responseDeferreds = {}

    def requestReceived(self, command, **kwargs):
        raise NotImplementedError

    def updateReceived(self, command, **kwargs):
        raise NotImplementedError

    def _requestReceived(self, key, command, **data):
        try:
            response = self.requestReceived(command, **data)
        except InvalidError as err:
            return self._sendResponse(key, 'invalid', message=str(err))
        except IllegalError as err:
            return self._sendResponse(key, 'illegal', message=str(err))
        except Exception as err:
            log.err(err)
            return self._sendResponse(key, 'internal', message=str(err))

        return self._sendResponse(key, 'success', **response)

    def jsonReceived(self, message):
        if message['type'] == 'request':
            self._requestReceived(
                message['key'],
                message['command'],
                **message['data'])
        elif message['type'] == 'response':
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
            self.updateReceived(message['command'], **message['data'])
        else:
            log.err('Message type not known: %s' % message['type'])

    def sendRequest(self, command, **kwargs):
        data = {
            'type': 'request',
            'key': generate_key(),
            'command': command,
            'data': kwargs,
        }
        self.sendJSON(data)

        d = q.Deferred()
        self._responseDeferreds[data['key']] = d
        return d.promise

    def _sendResponse(self, key, status, **kwargs):
        data = {
            'type': 'response',
            'key': key,
            'status': status,
            'data': kwargs,
        }
        self.sendJSON(data)

    def sendUpdate(self, command, **kwargs):
        data = {
            'type': 'update',
            'command': command,
            'data': kwargs,
        }
        self.sendJSON(data)


__all__ = ['InvalidError', 'IllegalError', 'Protocol']
