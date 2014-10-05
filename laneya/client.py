import sys

from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor

import protocol


def _print(s):
    print(s)


class ClientProtocol(protocol.ClientProtocol):
    def updateReceived(self, action, **kwargs):  # TODO
        print(action, kwargs)


def connected(protocol):  # TODO
    protocol.setup('testuser')

    protocol.sendRequest('echo', foo='bar')\
        .then(_print, log.err)

    protocol.sendRequest('other', foo='bar')\
        .then(_print, log.err)


def main():
    log.startLogging(sys.stdout)
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 5001)
    d = endpoint.connect(Factory.forProtocol(ClientProtocol))
    d.addCallbacks(connected, log.err)
    # q.fromTwisted(d).then(connected, log.err)
    reactor.run()


if __name__ == '__main__':  # pragma: nocover
    main()
