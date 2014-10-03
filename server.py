import sys

from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import protocol


class ServerProtocol(protocol.Protocol):
    def requestReceived(self, command, **kwargs):  # TODO
        if command == 'echo':
            return kwargs
        else:
            self.sendUpdate(command, **kwargs)
            return {}


def main():
    log.startLogging(sys.stdout)
    endpoint = TCP4ServerEndpoint(reactor, 5001)
    endpoint.listen(Factory.forProtocol(ServerProtocol))
    reactor.run()


if __name__ == '__main__':
    main()
