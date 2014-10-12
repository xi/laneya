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
        self.movable_layer = [[False for i in xrange(100)]for i in xrange(100)]

    def requestReceived(self, user, action, **kwargs):  # TODO
        if user not in self.users:
            self.users[user] = User()
            print("login %s" % user)

        if action == 'move':
            self.users[user].direction = kwargs['direction']
        elif action == 'logout':
            del self.users[user]
            print("logout %s" % user)
        else:
            raise protocol.InvalidError

    def mainloop(self):
        for key, user in self.users.iteritems():
            if user.direction == 'north':
                if collision_check(user.position_x, user.position_y-1):
                    self.movable_layer[user.position_x][user.position_y] = False
                    user.position_y -= 1
                    self.movable_layer[user.position_x][user.position_y] = user
                else:
                    raise protocol.IllegalError
            elif user.direction == 'east':
                # self.movable_layer[user.position_x][user.position_y] = False
                user.position_x += 1
                # self.movable_layer[user.position_x][user.position_y] = user
            elif user.direction == 'south':
                # self.movable_layer[user.position_x][user.position_y] = False
                user.position_y += 1
                # self.movable_layer[user.position_x][user.position_y] = user
            elif user.direction == 'west':
                # self.movable_layer[user.position_x][user.position_y] = False
                user.position_x -= 1
                # self.movable_layer[user.position_x][user.position_y] = user
            if user.direction != 'stop':
                self.broadcastUpdate(
                    'position',
                    x=user.position_x,
                    y=user.position_y,
                    entity=key)

    def collision_check(self, new_x, new_y):
        if self.movable_layer[newx][new_y] == False:
            return True
        else:
            return False

#  def move_user()


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
