class AttrString(unicode):
    def __new__(cls, s, **kwargs):
        self = super(AttrString, cls).__new__(cls, s)
        self.set_attrs(s, **kwargs)
        return self

    def set_attrs(self, reference, **kwargs):
        defaults = {
            'bold': False,
            'italic': False,
            'underline': False,
            'fg_color': (255, 255, 255),
            'bg_color': (0, 0, 0),
        }

        for attr in defaults.iterkeys():
            if attr in kwargs:
                value = kwargs[attr]
            elif isinstance(reference, AttrString):
                value = getattr(reference, attr)
            else:
                value = defaults[attr]

            setattr(self, attr, value)

    def get_attrs(self):
        return {
            'bold': self.bold,
            'italic': self.italic,
            'underline': self.underline,
            'fg_color': self.fg_color,
            'bg_color': self.bg_color,
        }

    def __iter__(self):
        return (self[i] for i in range(len(self)))

    def __getitem__(self, i):
        ch = unicode.__getitem__(self, i)
        return AttrString(ch, **self.get_attrs())


def normal(s):
    return unicode(s)


def bold(s):
    return AttrString(s, bold=True)


def italic(s):
    return AttrString(s, italic=True)


def underline(s):
    return AttrString(s, underline=True)


def white(s):
    return AttrString(s, fg_color=(255, 255, 255))


def black(s):
    return AttrString(s, fg_color=(0, 0, 0))


def red(s):
    return AttrString(s, fg_color=(255, 0, 0))


def green(s):
    return AttrString(s, fg_color=(0, 255, 0))


def blue(s):
    return AttrString(s, fg_color=(0, 0, 255))


def yellow(s):
    return AttrString(s, fg_color=(255, 255, 0))


def on_white(s):
    return AttrString(s, bg_color=(255, 255, 255))


def on_black(s):
    return AttrString(s, bg_color=(0, 0, 0))


def on_red(s):
    return AttrString(s, bg_color=(255, 0, 0))


def on_green(s):
    return AttrString(s, bg_color=(0, 255, 0))


def on_blue(s):
    return AttrString(s, bg_color=(0, 0, 255))


def on_yellow(s):
    return AttrString(s, bg_color=(255, 255, 0))
