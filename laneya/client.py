import trollius as asyncio

from dirtywords import Screen

import protocol

screen = Screen(40, 60)
screen.border()


class Client(protocol.ClientProtocolFactory):
    def __init__(self, loop):
        super(Client, self).__init__(loop)
        self.sprites = {}

    def connection_made(self):
        self.send_request('get_map', map_id='example_map')\
            .then(lambda response: self.render_floor(response['data']))

    def render_floor(self, data):
        floor_layer = data['floor_layer']
        width = len(floor_layer)
        height = len(floor_layer[0])

        def is_wall(x, y):
            return (
                x < 0 or x >= width or
                y < 0 or y >= height or
                floor_layer[x][y] == 'wall'
            )

        def sorrunded(x, y):
            return (
                is_wall(x - 1, y) and
                is_wall(x - 1, y - 1) and
                is_wall(x - 1, y + 1) and
                is_wall(x, y - 1) and
                is_wall(x + 1, y) and
                is_wall(x, y + 1) and
                is_wall(x + 1, y - 1) and
                is_wall(x + 1, y + 1)
            )

        for x, column in enumerate(floor_layer):
            for y, field in enumerate(column):
                if field == 'wall':
                    if not sorrunded(x, y):
                        screen.putstr(y, x, '#')

    def update_received(self, action, **kwargs):  # TODO
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
        return self.send_request('move', direction=direction)

    def mainloop(self):  # TODO
        for event in list(screen.get_key_events()):
            if event['key'] == ord('j'):
                self.move('south' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('k'):
                self.move('north' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('l'):
                self.move('east' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('h'):
                self.move('west' if event['type'] == 'keydown' else 'stop')
            elif event['key'] == ord('q'):
                self.send_request('logout')
                raise KeyboardInterrupt


def main():
    loop = asyncio.get_event_loop()

    client = Client(loop)
    client.setup('testuser')
    coro = loop.create_connection(client.build_protocol, 'localhost', 5001)
    loop.run_until_complete(coro)

    mainloop = protocol.LoopingCall(loop, client.mainloop)
    mainloop.start(0.02)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        screen.cleanup()
        loop.close()


if __name__ == '__main__':  # pragma: nocover
    main()
