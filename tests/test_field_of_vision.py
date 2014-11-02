from shared import unittest

from laneya import field_of_vision


class TestClosestToFarest(unittest.TestCase):
    def test_closest_to_farest(self):
        l = list(field_of_vision.closest_to_farest(3))
        self.assertListEqual(l, [
            (1, 0), (0, 1), (2, 0), (1, 1), (0, 2),
            (3, 0), (2, 1), (1, 2), (0, 3), (2, 2)])


class TestView(unittest.TestCase):
    def setUp(self):
        self.view = field_of_vision.View()

    def test_contains1(self):
        self.assertTrue(self.view.contains(1, 1))
        self.assertTrue(self.view.contains(0, 1))
        self.assertTrue(self.view.contains(1, 0))
        self.assertTrue(self.view.contains(100, 100))
        self.assertTrue(self.view.contains(0, 100))
        self.assertTrue(self.view.contains(100, 0))

    def test_contains2(self):
        self.view.steep_slope = 2
        self.view.shallow_slope = 0

        self.assertTrue(self.view.contains(1, 1))
        self.assertTrue(self.view.contains(10, 1))
        self.assertTrue(self.view.contains(3, 4))
        self.assertTrue(self.view.contains(300, 400))

        self.assertFalse(self.view.contains(0, 1))
        self.assertFalse(self.view.contains(0, 10))
        self.assertFalse(self.view.contains(1, 2))
        self.assertFalse(self.view.contains(5, 10))
        self.assertFalse(self.view.contains(1, 0))
        self.assertFalse(self.view.contains(10, 0))

    def test_split1(self):
        l = self.view.split(1, 1)
        self.assertEqual(len(l), 2)
        self.assertAlmostEqual(l[0].steep_slope, 1)
        self.assertEqual(l[0].shallow_slope, -1)
        self.assertEqual(l[1].steep_slope, -1)
        self.assertAlmostEqual(l[1].shallow_slope, 1)

    def test_split2(self):
        l = self.view.split(1, 0)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].steep_slope, -1)
        self.assertAlmostEqual(l[0].shallow_slope, 0)

    def test_split3(self):
        l = self.view.split(0, 1)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].steep_slope, float("inf"))
        self.assertAlmostEqual(l[0].shallow_slope, -1)

    def test_split4(self):
        l = self.view.split(4, 5)
        self.assertEqual(len(l), 2)
        self.assertAlmostEqual(l[0].steep_slope, 1.25)
        self.assertAlmostEqual(l[1].shallow_slope, 1.25)


class TestFieldOfVision(unittest.TestCase):
    def test_field_of_vision_simple(self):
        s = field_of_vision.field_of_vision(0, 0, 2, lambda x, y: False)
        self.assertSetEqual(s, set([
            (1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (-1, 0), (-2, 0), (-1, 1),
            (0, -1), (1, -1), (0, -2), (-1, -1)]))

    def test_field_of_vision_translated(self):
        s = field_of_vision.field_of_vision(1, 2, 2, lambda x, y: False)
        self.assertSetEqual(s, set([
            (2, 2), (1, 3), (3, 2), (2, 3), (1, 4), (0, 2), (-1, 2), (0, 3),
            (1, 1), (2, 1), (1, 0), (0, 1)]))

    def test_field_of_vision_blocking(self):
        s = field_of_vision.field_of_vision(0, 0, 2, lambda x, y: x > 0)
        self.assertSetEqual(s, set([
            (1, 0), (0, 1), (1, 1), (0, 2), (-1, 0), (-2, 0), (-1, 1),
            (0, -1), (1, -1), (0, -2), (-1, -1)]))

    def test_field_of_vision_blocking2(self):
        blocking = [
            (-4, 1), (-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1),
            (2, 1), (3, 1), (4, 1)]
        s = field_of_vision.field_of_vision(
            0, 0, 4, lambda x, y: (x, y) in blocking)
        self.assertSetEqual(s, set([
            (-4, 0),
            (-3, -2), (-3, -1), (-3, 0), (-3, 1),
            (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1),
            (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1),
            (0, -4), (0, -3), (0, -2), (0, -1), (0, 1),
            (1, -3), (1, -2), (1, -1), (1, 0), (1, 1),
            (2, -3), (2, -2), (2, -1), (2, 0), (2, 1),
            (3, -2), (3, -1), (3, 0), (3, 1),
            (4, 0)]))
