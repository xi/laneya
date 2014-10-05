import sys

from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import protocol


class ServerProtocol(protocol.ServerProtocol):
    def requestReceived(self, user, action, **kwargs):  # TODO
        if action == 'echo':
            return kwargs
        else:
            self.broadcastUpdate(action, **kwargs)
            reactor.callLater(5, self.broadcastUpdate, action, **kwargs)
            return {}


def main():
    log.startLogging(sys.stdout)
    endpoint = TCP4ServerEndpoint(reactor, 5001)
    endpoint.listen(protocol.ServerProtocolFactory(ServerProtocol))
    reactor.run()


if __name__ == '__main__':  # pragma: nocover
    main()
