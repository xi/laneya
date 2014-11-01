# from twisted.python import log
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor
from twisted.internet import task

from dirtywords import Screen

import protocol

screen = Screen(40, 60)
screen.border()


class Client(protocol.ClientProtocolFactory):
    def __init__(self):
        protocol.ClientProtocolFactory.__init__(self)
        self.sprites = {}

    def connectionMade(self):
        self.sendRequest('get_map', map_id='example_map')\
            .then(lambda response: self.render_floor(response['data']))

    def render_floor(self, data):
        floor_layer = data['floor_layer']
        width = len(floor_layer)
        height = len(floor_layer[0])

        is_wall = lambda x, y: (
            x < 0 or x >= width or
            y < 0 or y >= height or
            floor_layer[x][y] == 'wall')

        sorrunded = lambda x, y: (
            is_wall(x - 1, y) and
            is_wall(x - 1, y - 1) and
            is_wall(x - 1, y + 1) and
            is_wall(x, y - 1) and
            is_wall(x + 1, y) and
            is_wall(x, y + 1) and
            is_wall(x + 1, y - 1) and
            is_wall(x + 1, y + 1))

        for x, column in enumerate(floor_layer):
            for y, field in enumerate(column):
                if field == 'wall':
                    if not sorrunded(x, y):
                        screen.putstr(y, x, '#')

    def updateReceived(self, action, **kwargs):  # TODO
        if action == 'position':
            entity = kwargs['entity']
            if entity not in self.sprites:
                self.sprites[entity] = {}
            else:
                screen.delch(
                    self.sprites[entity]['y'],
                    self.sprites[entity]['x'])
            self.sprites[entity]['x'] = kwargs['x']
            self.sprites[entity]['y'] = kwargs['y']
            screen.putstr(kwargs['y'], kwargs['x'], entity[0])
        screen.refresh()

    def move(self, direction):
        return self.sendRequest('move', direction=direction)

    def mainloop(self):  # TODO
        for event in screen.get_key_events():
            if event['key'] == ord('j'):
                self.move('south' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('k'):
                self.move('north' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('l'):
                self.move('east' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('h'):
                self.move('west' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('q'):
                self.sendRequest('logout')
                screen.cleanup()
                reactor.stop()


def main():
    # log.startLogging(sys.stdout)
    client = Client()
    client.setup('testuser')
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 5001)
    endpoint.connect(client)

    mainloop = task.LoopingCall(client.mainloop)
    mainloop.start(0.02)

    reactor.run()


if __name__ == '__main__':  # pragma: nocover
    main()
