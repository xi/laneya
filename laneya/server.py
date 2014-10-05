import sys

from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.internet import task

import protocol


class User(object):
    def __init__(self, position_x=0, position_y=0, direction='stop'):
        self.position_x = position_x
        self.position_y = position_y
        self.direction = direction


class Server(protocol.ServerProtocolFactory):
    def __init__(self):
        protocol.ServerProtocolFactory.__init__(self)
        self.users = {}

    def requestReceived(self, user, action, **kwargs):  # TODO
        if user not in self.users:
            self.users[user] = User()
            print("login %s" % user)

        if action == 'move':
            self.users[user].direction = kwargs['direction']
            return {}
        elif action == 'logout':
            del self.users[user]
            print("logout %s" % user)
            return {}
        else:
            raise protocol.InvalidError

    def mainloop(self):
        for key, user in self.users.iteritems():
            if user.direction == 'north':
                user.position_y -= 1
            elif user.direction == 'east':
                user.position_x += 1
            elif user.direction == 'south':
                user.position_y += 1
            elif user.direction == 'west':
                user.position_x -= 1
            if user.direction != 'stop':
                self.broadcastUpdate(
                    'position',
                    x=user.position_x,
                    y=user.position_y,
                    entity=key)


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
