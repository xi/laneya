"""Collection of available actions.

This module describes the available actions.  The actions are modelled as
functions that may perform arbitrary validation on the incoming data.

The actual processing of actions happens in the server and client.

"""


def echo(foo=''):
    """Example server action."""


def other(foo=''):
    """Example client action."""


def move(direction=None):
    """Start moving in the defined direction.

    This message is primarily useful for clients that want to move their users
    on the map.  They can easily convert key press events to ``move``
    messages.

    I might be worth to also broadcast these messages so clients can
    interpolate a user's movement.  ``move`` messages are however not fit to
    handle the actual movement of entities because clients may run with
    different speeds. The ``position`` message should be used instead.

    """
    assert direction in ['north', 'east', 'south', 'west', 'stop']


def position(x=None, y=None, entity=None):
    """Set an entities position."""
    assert isinstance(x, int)
    assert isinstance(y, int)


def logout():
    """Delete the requesting user.

    There is no explicit login.  The user is created on her initial request.
    """
