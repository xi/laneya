import sys

from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.internet import task

import protocol


class ServerProtocol(protocol.ServerProtocol):
    def requestReceived(self, user, action, **kwargs):  # TODO
        if action == 'echo':
            return kwargs
        else:
            self.broadcastUpdate(action, **kwargs)
            reactor.callLater(5, self.broadcastUpdate, action, **kwargs)
            return {}


class Server(protocol.ServerProtocolFactory):
    def __init__(self):
        protocol.ServerProtocolFactory.__init__(self, ServerProtocol)

    def mainloop(self):
        self.broadcastUpdate('echo', foo='mainloop')


def main():
    log.startLogging(sys.stdout)
    server = Server()
    endpoint = TCP4ServerEndpoint(reactor, 5001)
    endpoint.listen(server)

    mainloop = task.LoopingCall(server.mainloop)
    mainloop.start(0.1)

    reactor.run()


if __name__ == '__main__':  # pragma: nocover
    main()
