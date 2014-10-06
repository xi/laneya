# flake8: noqa

try:
    from pygame_dirtywords import Screen
except ImportError:
    try:
        from curses_dirtywords import Screen
    except ImportError:
        from stupid_dirtywords import Screen

from base import Window
