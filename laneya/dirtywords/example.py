import sys

try:
    from pygame_dirtywords import Screen
except ImportError:
    try:
        from curses_dirtywords import Screen
    except ImportError:
        from stupid_dirtywords import Screen

from attr_string import italic
from attr_string import blue


class Player(object):
    def __init__(self, win):
        self.win = win
        self.y = win.height / 2
        self.x = win.width / 2

    def move(self, direction):
        self.win.putstr(self.y, self.x, ' ')

        if direction == 'up':
            self.y -= 1
        elif direction == 'right':
            self.x += 1
        elif direction == 'down':
            self.y += 1
        elif direction == 'left':
            self.x -= 1

        self.win.putstr(self.y, self.x, italic(blue('X')))
        self.win.refresh()


if __name__ == '__main__':
    scr = Screen(32, 100)

    try:
        scr.border()

        player = Player(scr)
        player.move('down')  # initial refresh

        while 1:
            ch = scr.getch()
            if ch == ord('h'):
                player.move('left')
            elif ch == ord('j'):
                player.move('down')
            elif ch == ord('k'):
                player.move('up')
            elif ch == ord('l'):
                player.move('right')
            elif ch == ord('q'):
                scr.cleanup()
                sys.exit()
    except:
        scr.cleanup()
        raise
