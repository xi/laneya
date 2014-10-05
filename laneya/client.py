import sys

from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor

import protocol
import deferred as q


def _print(s):
    print(s)


class ClientProtocol(protocol.ClientProtocol):
    def updateReceived(self, action, **kwargs):  # TODO
        print(action, kwargs)

    def move(self, direction):
        return self.sendRequest('move', direction=direction)


def connected(protocol):  # TODO
    protocol.setup('testuser')

    protocol.sendRequest('echo', foo='bar')\
        .then(_print, log.err)

    protocol.sendRequest('other', foo='bar')\
        .then(_print, log.err)

    protocol.move('south')
    reactor.callLater(2, lambda: protocol.move('west'))
    reactor.callLater(4, lambda: protocol.move('north'))
    reactor.callLater(6, lambda: protocol.move('east'))
    reactor.callLater(8, lambda: protocol.move('stop'))

    reactor.callLater(10, lambda: protocol.sendRequest('logout'))


def main():
    log.startLogging(sys.stdout)
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 5001)
    d = endpoint.connect(Factory.forProtocol(ClientProtocol))
    q.fromTwisted(d).then(connected, log.err)
    reactor.run()


if __name__ == '__main__':  # pragma: nocover
    main()
