class BaseScreen(object):
    def __init__(self, height, width):
        """Initialize screen."""
        self.height = height
        self.width = width
        self.data = [[' ' for xx in range(width)] for yy in range(height)]

    def getch(self):
        """Get next keystroke (blocking)."""
        raise NotImplementedError

    def putstr(self, y, x, s):
        """Write string to position."""
        for i, ch in enumerate(s):
            try:
                self.data[y][x + i] = ch
            except IndexError:
                pass

    def refresh(self):
        """Print the current state to the screen."""
        raise NotImplementedError

    def cleanup(self):
        """Deinitialize screen."""
        pass


class Screen(BaseScreen):
    """Additional utility functions for :py:class:`BaseScreen`."""

    def delch(self, y, x):
        """Delete character at position."""
        self.putstr(y, x, ' ')

    def fill_row(self, y, ch):
        """Fill a complete row with character."""
        self.putstr(y, 0, ch * self.width)

    def fill_column(self, x, ch):
        """Fill a complete column with character."""
        for y in range(self.height):
            self.putstr(y, x, ch)

    def fill(self, ch):
        """Fill whole screen with character."""
        for y in range(self.height):
            self.row(y, ch)

    def clear(self):
        """Clear whole screen."""
        self.fill(' ')

    def border(self, ls='|', rs='|', ts='-', bs='-',
               tl='+', tr='+', bl='+', br='+'):
        """Draw border around screen."""
        self.fill_column(0, ls)
        self.fill_column(self.width - 1, rs)
        self.fill_row(0, ts)
        self.fill_row(self.height - 1, bs)
        self.putstr(0, 0, tl)
        self.putstr(0, self.width - 1, tr)
        self.putstr(self.height - 1, 0, bl)
        self.putstr(self.height - 1, self.width - 1, br)


class Window(Screen):
    """A screen that is rendered onto another screen."""

    def __init__(self, parent, height, width, y, x):
        super(Window, self).__init__(height, width)
        self.parent = parent
        self.y = y
        self.x = x

    def getch(self):
        return self.parent.getch()

    def refresh(self):
        for y in range(self.height):
            for x in range(self.width):
                self.parent.putstr(self.y + y, self.x + x, self.data[y][x])
        self.parent.refresh()
