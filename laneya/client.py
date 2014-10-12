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
        self.position_x = 0
        self.position_y = 0

    def updateReceived(self, action, **kwargs):  # TODO
        if action == 'position':
            screen.delch(self.position_y, self.position_x)
            self.position_x = kwargs['x']
            self.position_y = kwargs['y']
            screen.putstr(self.position_y, self.position_x, 'X')
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
