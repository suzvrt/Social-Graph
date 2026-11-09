import itertools
import random
import unittest

from socialgraph.config import EDGE_CLEARANCE
from socialgraph.ui.geometry import (distance, force_layout, point_segment_distance, quadratic_bezier,
                                     route_edge)

R = 35


def min_clearance(route, obstacles, samples=64):
    """Smallest distance between the drawn route and any obstacle center."""
    if route.curved:
        a, c, b = route.points
        points = [quadratic_bezier(a, c, b, i / samples) for i in range(samples + 1)]
    else:
        points = route.points
    return min(point_segment_distance(o, p, q) for o in obstacles for p, q in zip(points, points[1:]))


class DistanceTests(unittest.TestCase):
    def test_point_segment_distance(self):
        self.assertAlmostEqual(point_segment_distance((5, 5), (0, 0), (10, 0)), 5)
        self.assertAlmostEqual(point_segment_distance((-3, 4), (0, 0), (10, 0)), 5)
        self.assertAlmostEqual(point_segment_distance((1, 1), (0, 0), (0, 0)), 2 ** 0.5)


class RouteTests(unittest.TestCase):
    def test_free_path_is_a_straight_line_between_borders(self):
        route = route_edge((0, 0), (300, 0), R)
        self.assertFalse(route.curved)
        self.assertEqual(route.points, [(R, 0), (300 - R, 0)])
        self.assertEqual(route.label, (150, 0))

    def test_edge_through_a_vertex_curves_around_it(self):
        obstacle = (150, 5)
        route = route_edge((0, 0), (300, 0), R, [obstacle])
        self.assertTrue(route.curved)
        self.assertGreaterEqual(min_clearance(route, [obstacle]), R + EDGE_CLEARANCE - 1)
        # The obstacle sits slightly below the line, so the curve bends upwards (negative y).
        self.assertLess(route.points[1][1], 0)
        self.assertAlmostEqual(distance(route.points[0], (0, 0)), R)
        self.assertAlmostEqual(distance(route.points[2], (300, 0)), R)

    def test_fully_blocked_edge_still_avoids_the_vertex_on_its_line(self):
        wall = [(150, y) for y in range(-300, 301, 60)]
        route = route_edge((0, 0), (300, 0), R, wall)
        self.assertTrue(route.curved)
        self.assertGreater(min_clearance(route, wall), 0)

    def test_bidirectional_pair_is_drawn_on_separate_sides(self):
        forward = route_edge((0, 0), (300, 0), R, bidirectional=True)
        backward = route_edge((300, 0), (0, 0), R, bidirectional=True)
        self.assertNotEqual(forward.points[0][1], backward.points[-1][1])
        self.assertGreater(distance(forward.label, backward.label), 20)
        for point, center in ((forward.points[0], (0, 0)), (forward.points[1], (300, 0))):
            self.assertAlmostEqual(distance(point, center), R)

    def test_coincident_vertices_do_not_crash(self):
        self.assertFalse(route_edge((10, 10), (10, 10), R).curved)


class LayoutTests(unittest.TestCase):
    def test_vertices_stay_inside_margins_and_apart(self):
        vertices = ["v%d" % i for i in range(12)]
        edges = [(vertices[i], vertices[(i + 1) % 12]) for i in range(12)]
        width, height, margin = 960, 540, R + 5
        for seed in range(20):
            with self.subTest(seed=seed):
                positions = force_layout(vertices, edges, width, height, margin, min_distance=3 * R,
                                         rng=random.Random(seed))
                self.assertCountEqual(positions, vertices)
                for x, y in positions.values():
                    self.assertTrue(margin <= x <= width - margin and margin <= y <= height - margin)
                closest = min(distance(p, q) for p, q in itertools.combinations(positions.values(), 2))
                self.assertGreater(closest, 2 * R)

    def test_same_seed_gives_same_layout(self):
        args = (["a", "b", "c"], [("a", "b")], 500, 400, 40)
        self.assertEqual(force_layout(*args, rng=random.Random(7)), force_layout(*args, rng=random.Random(7)))

    def test_empty_graph(self):
        self.assertEqual(force_layout([], [], 500, 400, 40), {})


if __name__ == "__main__":
    unittest.main()
