import sys

import base


class Screen(base.Screen):
    def getch(self):
        # http://code.activestate.com/recipes/134892/

        try:
            import msvcrt
            return msvcrt.getch()
        except ImportError:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ord(ch)

    def refresh(self):
        spacing = '\n' * self.height * 2
        s = '\n'.join([''.join(row) for row in self.data])
        print(spacing + s)
