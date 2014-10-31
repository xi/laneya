import random

import protocol


class Map(object):
    """A singel map containing sprites.

    The map object takes care of managing all sprites within one map. As only
    very few actions involve multiple maps (e.g. moving from one map to
    another) this covers a lot of the game logic.

    The passed server is used to send updates to the clients.

    Map objects expose an API for the server (e.g. :py:meth:`step`) and another
    one for sprites (e.g. :py:meth:`move_sprite`).

    """
    def __init__(self, server):
        self.server = server
        self.sprites = {}
        self.movable_layer = [[None for i in xrange(100)] for i in xrange(100)]
        self.ghost = Ghost('example', self, 15, 15)

    def step(self):
        """Update this map and all of its sprites.

        If this map is currently active (contains at least on user), the server
        should call this method once per mainloop cycle.

        """
        for sprite in self.sprites.itervalues():
            sprite.step()

    def is_collision_free(self, x, y):
        """Check whether a sprite can move to field (x, y)."""
        return self.movable_layer[x][y] is None

    def move_sprite(self, sprite, dx, dy):
        """Move a sprite."""
        if self.is_collision_free(sprite.x + dx, sprite.y + dy):
            self.movable_layer[sprite.x][sprite.y] = None
            sprite.x += dx
            sprite.y += dy
            self.movable_layer[sprite.x][sprite.y] = sprite
            self.server.broadcastUpdate(
                'position',
                x=sprite.x,
                y=sprite.y,
                entity=sprite.id)
        else:
            raise protocol.IllegalError


class Sprite(object):
    """Simple base class for visible game objects."""

    def __init__(self, name, _map, x, y):
        self.id = "%s:%s" % (self.__class__.__name__, name)
        self.map = _map
        self.x = x
        self.y = y

        self.map.sprites[self.id] = self

    def kill(self):
        """Remove this sprite from the map."""
        del self.map.sprites[self.id]

    def step(self):
        """Update this sprite.

        This function is executed once per mainloop cycle. Subclasses should
        overwrite this in order to define custom behavior.

        """
        pass

    def interact(self, other):
        """Interact with this sprite.

        Subclasses should overwrite this in order to define custom
        interactions.

        """
        pass


class MovingSprite(Sprite):
    """A sprite that can move.

    You can set :py:attr:`direction` to one of 'north', 'east', 'south', 'west'
    or 'stop'.  This sprite will then automatically move one filed in the
    specified direction in every mainloop cycle.

    """

    def __init__(self, *args, **kwargs):
        super(MovingSprite, self).__init__(*args, **kwargs)
        self.direction = 'stop'

    def step(self):
        if self.direction == 'north':
            self.map.move_sprite(self, 0, -1)
        elif self.direction == 'east':
            self.map.move_sprite(self, 1, 0)
        elif self.direction == 'south':
            self.map.move_sprite(self, 0, 1)
        elif self.direction == 'west':
            self.map.move_sprite(self, -1, 0)


class User(MovingSprite):
    """Sprite representing a user."""


class Ghost(MovingSprite):
    def step(self):
        self.direction = random.choice(
            ['north', 'east', 'south', 'west', 'stop'])
        super(Ghost, self).step()


__all__ = ['Map', 'Sprite', 'MovingSprite', 'User']
