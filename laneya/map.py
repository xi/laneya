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
    def __init__(self, server, width=60, height=40):
        self.server = server
        self.width = width
        self.height = height
        self.sprites = {}
        self.movable_layer = [
            [None for i in xrange(height)] for i in xrange(width)]
        self.floor_layer = [
            [None for i in xrange(height)] for i in xrange(width)]
        self.generate()
        self.ghost = Ghost('example', self, 15, 15)

    def generate(self):
        rooms = []

        # make sure user and ghost are inside of a room
        rooms.append({
            'x_min': 5,
            'x_max': 20,
            'y_min': 5,
            'y_max': 20,
        })

        for i in range(2000):
            x1 = random.randint(1, self.width - 2)
            x2 = random.randint(1, self.width - 2)
            y1 = random.randint(1, self.height - 2)
            y2 = random.randint(1, self.height - 2)

            room = {
                'x_min': min(x1, x2),
                'x_max': max(x1, x2),
                'y_min': min(y1, y2),
                'y_max': max(y1, y2),
            }

            collision_free = lambda other: (
                room['x_min'] > other['x_max'] + 1 or
                room['x_max'] < other['x_min'] - 1 or
                room['y_min'] > other['y_max'] + 1 or
                room['y_max'] < other['y_min'] - 1)

            if (room['x_max'] - room['x_min'] > 2 and
                    room['y_max'] - room['y_min'] > 2):
                if all((collision_free(other) for other in rooms)):
                    rooms.append(room)

        in_room = lambda x, y, room: (
            x >= room['x_min'] and
            x <= room['x_max'] and
            y >= room['y_min'] and
            y <= room['y_max'])

        # carve rooms
        for x in range(self.width):
            for y in range(self.height):
                if any((in_room(x, y, room) for room in rooms)):
                    self.floor_layer[x][y] = 'floor'
                else:
                    self.floor_layer[x][y] = 'wall'

        # carve paths
        for i, room in enumerate(rooms):
            if i != 0:
                last = rooms[i - 1]

                x_center = (room['x_max'] + room['x_min']) / 2
                y_center = (room['y_max'] + room['y_min']) / 2
                last_x_center = (last['x_max'] + last['x_min']) / 2
                last_y_center = (last['y_max'] + last['y_min']) / 2

                x_min = min(x_center, last_x_center)
                x_max = max(x_center, last_x_center) + 1
                y_min = min(y_center, last_y_center)
                y_max = max(y_center, last_y_center) + 1

                for x in range(x_min, x_max):
                    self.floor_layer[x][last_y_center] = 'floor'

                for y in range(y_min, y_max):
                    self.floor_layer[x_center][y] = 'floor'

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

    def encode(self):
        return {
            'floor_layer': self.floor_layer,
        }

    def decode(self, data):
        self.floor_layer = data['floor_layer']


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
