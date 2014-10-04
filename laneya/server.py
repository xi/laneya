import sys

from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import protocol


class ServerProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.connections.append(self)

    def connectionLost(self, reason):
        self.factory.connections.remove(self)

    def broadcastUpdate(self, command, **kwargs):
        """Broadcast an update to all connected clients."""

        for connection in self.factory.connections:
            connection.sendUpdate(command, **kwargs)

    def requestReceived(self, command, **kwargs):  # TODO
        if command == 'echo':
            return kwargs
        else:
            self.broadcastUpdate(command, **kwargs)
            return {}


class ServerProtocolFactory(Factory):
    def __init__(self):
        self.connections = []

    def buildProtocol(self, addr):
        return ServerProtocol(self)


def main():
    log.startLogging(sys.stdout)
    endpoint = TCP4ServerEndpoint(reactor, 5001)
    endpoint.listen(ServerProtocolFactory())
    reactor.run()


if __name__ == '__main__':  # pragma: nocover
    main()
