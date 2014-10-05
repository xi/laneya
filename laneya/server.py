import sys

from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.internet import task

import protocol


class ServerProtocol(protocol.ServerProtocol):
    def requestReceived(self, user, action, **kwargs):  # TODO
        if user not in self.factory.users:
            self.factory.users[user] = {}

        if action == 'echo':
            return kwargs
        elif action == 'move':
            self.factory.direction = kwargs['direction']
            return {}
        else:
            self.broadcastUpdate(action, **kwargs)
            reactor.callLater(5, self.broadcastUpdate, action, **kwargs)
            return {}


class Server(protocol.ServerProtocolFactory):
    def __init__(self):
        protocol.ServerProtocolFactory.__init__(self, ServerProtocol)
        self.users = {}

        # TODO: should be set per user
        self.direction = 'stop'
        self.position_x = 0
        self.position_y = 0

    def mainloop(self):
        if self.direction == 'north':
            self.position_y -= 1
        elif self.direction == 'east':
            self.position_x += 1
        elif self.direction == 'south':
            self.position_y += 1
        elif self.direction == 'west':
            self.position_x -= 1
        if self.direction != 'stop':
            self.broadcastUpdate(
                'position',
                x=self.position_x,
                y=self.position_y,
                entity='example')


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
