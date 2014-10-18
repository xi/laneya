import trollius as asyncio

from dirtywords import Screen

import protocol

screen = Screen(40, 60)
screen.border()


class Client(protocol.ClientProtocolFactory):
    def __init__(self, loop):
        super(Client, self).__init__(loop)
        self.position_x = 0
        self.position_y = 0

    def update_received(self, action, **kwargs):  # TODO
        if action == 'position':
            screen.delch(self.position_y, self.position_x)
            self.position_x = kwargs['x']
            self.position_y = kwargs['y']
            screen.putstr(self.position_y, self.position_x, 'X')
        screen.refresh()

    def move(self, direction):
        return self.send_request('move', direction=direction)

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
                self.send_request('logout')
                screen.cleanup()
                self.loop.close()


def main():
    loop = asyncio.get_event_loop()

    client = Client(loop)
    client.setup('testuser')
    coro = loop.create_connection(client.build_protocol, 'localhost', 5001)
    loop.run_until_complete(coro)

    mainloop = protocol.LoopingCall(loop, client.mainloop)
    mainloop.start(0.02)

    loop.run_forever()


if __name__ == '__main__':  # pragma: nocover
    main()
