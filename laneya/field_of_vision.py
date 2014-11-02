# Inspired by
# http://www.roguebasin.com/index.php?title=Precise_Permissive_Field_of_View

QUADRANTS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

# coordinates represent the lower left corner of fields


class View(object):
    def __init__(self, steep_slope=-1, shallow_slope=-1):
        self.steep_slope = steep_slope
        self.shallow_slope = shallow_slope

    def contains(self, x, y):
        return (
            (self.steep_slope * x > y or self.steep_slope < 0) and
            (self.shallow_slope * x < y or self.shallow_slope < 0))

    def split(self, x, y):
        new_slope = float(y) / x if x > 0 else float("inf")

        ret = []
        if self.shallow_slope * (x + 1) < y - 1 and new_slope > 0:
            ret.append(View(new_slope, self.shallow_slope))
        if ((self.steep_slope < 0 or self.steep_slope * (x - 1) > y + 1)
                and new_slope < float("inf")):
            ret.append(View(self.steep_slope, new_slope))
        return ret


def closest_to_farest(radius):
    for _dx in xrange(radius * 2 + 1):
        for dy in xrange(_dx + 1):
            dx = _dx - dy
            if dx ** 2 + dy ** 2 <= radius ** 2:
                if dx != 0 or dy != 0:
                    yield dx, dy


def field_of_vision(center_x, center_y, radius, blocks_view):
    """Calculate field of vision.

    ``center_x`` and ``center_y`` are the coordinates of the player.
    ``radius`` is the maximum distance the player can see.
    ``blocks_view`` is a function that returns a boolean signifying whether
    there is something blocking the view at the specified coordinates.

    """
    visible = set()
    for quadrant in QUADRANTS:
        new_views = [View()]

        for dx, dy in closest_to_farest(radius):
            x = center_x + quadrant[0] * dx
            y = center_y + quadrant[1] * dy

            views = new_views
            new_views = []

            for view in views:
                if view.contains(dx, dy):
                    visible.add((x, y))

                if view.contains(dx, dy) and blocks_view(x, y):
                    new_views += view.split(dx, dy)
                else:
                    new_views.append(view)

    return visible


__all__ = ['field_of_vision']
