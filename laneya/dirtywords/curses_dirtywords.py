try:
    from ncurses import curses
except ImportError:
    import curses

import base


class Screen(base.Screen):
    def __init__(self, height, width):
        self.height = height
        self.width = width

        curses.initscr()
        curses.noecho()
        curses.curs_set(0)
        self.curses_window = curses.newwin(height, width, 0, 0)

    def getch(self):
        return self.curses_window.getch()

    def putstr(self, y, x, s):
        for i, ch in enumerate(s):
            try:
                self.curses_window.addstr(y, x + i, ch)
            except:
                pass

    def refresh(self):
        self.curses_window.refresh()

    def cleanup(self):
        curses.endwin()
