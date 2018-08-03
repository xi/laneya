import trollius as asyncio

from . import protocol
from .map import MapManager, User


class Server(protocol.ServerProtocolFactory):
    def __init__(self):
        protocol.ServerProtocolFactory.__init__(self)
        self.users = {}
        self.map_manager = MapManager(self, 60, 40)

    def request_received(self, user, action, **kwargs):  # TODO
        if user not in self.users:
            initial_map = self.map_manager.get(0, 0, 0)
            self.users[user] = User(user, initial_map, 10, 10)
            print("login %s" % user)

        if action == 'move':
            self.users[user].direction = kwargs['direction']
        elif action == 'logout':
            self.users[user].kill()
            del self.users[user]
            print("logout %s" % user)
        elif action == 'get_map':
            return self.users[user].map.encode()
        else:
            raise protocol.InvalidError

    def mainloop(self):
        # only the maps with users in them get updated
        for _map in self.get_active_maps():
            _map.step()

    def get_active_maps(self):
        return set([user.map for user in self.users.values()])


def main():
    loop = asyncio.get_event_loop()

    server = Server()
    coro = loop.create_server(server.build_protocol, 'localhost', 5001)
    s = loop.run_until_complete(coro)

    mainloop = protocol.LoopingCall(loop, server.mainloop)
    mainloop.start(0.1)

    try:
        loop.run_forever()
    finally:
        s.close()
        loop.run_until_complete(s.wait_closed())
        loop.close()


if __name__ == '__main__':  # pragma: nocover
    main()
