import sys

from twisted.python import log
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor
from twisted.internet import task

import protocol
import deferred as q


class Client(protocol.ClientProtocolFactory):
    def updateReceived(self, action, **kwargs):  # TODO
        print(action, kwargs)

    def move(self, direction):
        return self.sendRequest('move', direction=direction)

    def connected(self, protocol):  # TODO
        self.move('south')
        reactor.callLater(2, lambda: self.move('west'))
        reactor.callLater(4, lambda: self.move('north'))
        reactor.callLater(6, lambda: self.move('east'))
        reactor.callLater(8, lambda: self.move('stop'))

        reactor.callLater(10, lambda: self.sendRequest('logout'))

    def mainloop(self):  # TODO
        pass


def main():
    log.startLogging(sys.stdout)
    client = Client()
    client.setup('testuser')
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 5001)
    d = endpoint.connect(client)
    q.fromTwisted(d).then(client.connected, log.err)

    mainloop = task.LoopingCall(client.mainloop)
    mainloop.start(0.1)

    reactor.run()


if __name__ == '__main__':  # pragma: nocover
    main()
