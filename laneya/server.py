import sys

from twisted.python import log
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.internet import task

import protocol
from map import Map, User


class Server(protocol.ServerProtocolFactory):
    def __init__(self):
        protocol.ServerProtocolFactory.__init__(self)
        self.users = {}
        self.map = Map(self)  # TODO: more than one map

    def requestReceived(self, user, action, **kwargs):  # TODO
        if user not in self.users:
            self.users[user] = User(user, self.map, 10, 10)
            print("login %s" % user)

        if action == 'move':
            self.users[user].direction = kwargs['direction']
        elif action == 'logout':
            self.users[user].kill()
            del self.users[user]
            print("logout %s" % user)
        elif action == 'get_map':
            return self.map.encode()
        else:
            raise protocol.InvalidError

    def mainloop(self):
        # only the maps with users in them get updated
        for _map in self.get_active_maps():
            _map.step()

    def get_active_maps(self):
        return set([user.map for user in self.users.itervalues()])


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
