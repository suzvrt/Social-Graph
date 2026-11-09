"""Pure 2D geometry for edge routing and automatic layout.

Kept free of Tk so it can be unit tested. Points are (x, y) tuples.
"""

import math
import random
from typing import List, NamedTuple, Tuple

from socialgraph.config import EDGE_BENDS, EDGE_CLEARANCE, EDGE_PAIR_OFFSET, LAYOUT_ITERATIONS

Point = Tuple[float, float]

_CURVE_SAMPLES = 16
# Shifts each label of a bidirectional pair towards its own destination so the two don't overlap.
_PAIR_LABEL_SHIFT = 12


class Route(NamedTuple):
    """How to draw an edge: points for create_line (3 points means a curve) and the label position."""

    points: List[Point]
    label: Point
    curved: bool


def distance(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def point_segment_distance(p, a, b):
    """Shortest distance from point p to the segment a-b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return distance(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq))
    return distance(p, (a[0] + t * dx, a[1] + t * dy))


def quadratic_bezier(a, c, b, t):
    """Point at parameter t of the curve Tk draws for create_line(a, c, b, smooth=True)."""
    u = 1 - t
    return (u * u * a[0] + 2 * u * t * c[0] + t * t * b[0],
            u * u * a[1] + 2 * u * t * c[1] + t * t * b[1])


def route_distance(route, point):
    """Distance from point to the drawn route (sampling the curve if it is one)."""
    if route.curved:
        a, c, b = route.points
        polyline = [quadratic_bezier(a, c, b, i / _CURVE_SAMPLES) for i in range(_CURVE_SAMPLES + 1)]
    else:
        polyline = route.points
    return _clearance(polyline, [point])


def _border_towards(center, target, radius):
    d = distance(center, target) or 1.0
    return (center[0] + radius * (target[0] - center[0]) / d,
            center[1] + radius * (target[1] - center[1]) / d)


def _clearance(polyline, obstacles):
    """Smallest distance between the polyline and any obstacle center."""
    return min((point_segment_distance(o, p, q) for o in obstacles for p, q in zip(polyline, polyline[1:])),
               default=math.inf)


def route_edge(src, dst, radius, obstacles=(), bidirectional=False):
    """Route the arrow src -> dst between the borders of two circles of the given radius.

    obstacles are the centers of the other circles. If the straight line passes
    through one of them, the edge becomes a curve bent to whichever side is free;
    if no bend is fully clear, the one passing farthest from the obstacles wins.
    When the reverse edge also exists, each one is shifted to its own side so both stay visible.
    """
    length = distance(src, dst)
    if length == 0:
        return Route([src, src], src, False)
    ux, uy = (dst[0] - src[0]) / length, (dst[1] - src[1]) / length
    # Normal pointing to the edge's own side; it flips for the reverse edge.
    nx, ny = -uy, ux

    offset = EDGE_PAIR_OFFSET if bidirectional else 0.0
    along = math.sqrt(max(radius * radius - offset * offset, 0.0))
    a = (src[0] + nx * offset + ux * along, src[1] + ny * offset + uy * along)
    b = (dst[0] + nx * offset - ux * along, dst[1] + ny * offset - uy * along)
    shift = _PAIR_LABEL_SHIFT if bidirectional else 0.0
    straight = Route([a, b], ((a[0] + b[0]) / 2 + ux * shift, (a[1] + b[1]) / 2 + uy * shift), False)

    limit = radius + EDGE_CLEARANCE
    # A quadratic curve strays at most half its bend from the chord, so farther vertices can't matter.
    reach = limit + offset + max(EDGE_BENDS) / 2
    obstacles = [o for o in obstacles if point_segment_distance(o, src, dst) < reach]
    best, best_clearance = straight, _clearance([a, b], obstacles)
    if best_clearance >= limit:
        return straight

    if bidirectional:
        sides = (1, -1)
    else:
        nearest = min(obstacles, key=lambda o: point_segment_distance(o, a, b))
        away = -1 if (nearest[0] - src[0]) * nx + (nearest[1] - src[1]) * ny > 0 else 1
        sides = (away, -away)

    mid = ((src[0] + dst[0]) / 2 + nx * offset, (src[1] + dst[1]) / 2 + ny * offset)
    for bend in EDGE_BENDS:
        for side in sides:
            control = (mid[0] + nx * side * bend, mid[1] + ny * side * bend)
            ca, cb = _border_towards(src, control, radius), _border_towards(dst, control, radius)
            samples = [quadratic_bezier(ca, control, cb, i / _CURVE_SAMPLES) for i in range(_CURVE_SAMPLES + 1)]
            clearance = _clearance(samples, obstacles)
            if clearance > best_clearance:
                best = Route([ca, control, cb], quadratic_bezier(ca, control, cb, 0.5), True)
                best_clearance = clearance
            if clearance >= limit:
                return best
    return best


def force_layout(vertices, edges, width, height, margin, min_distance=0.0, iterations=LAYOUT_ITERATIONS,
                 rng=None):
    """Fruchterman-Reingold spring layout.

    Connected vertices attract, every pair repels, and the step size cools down
    each iteration. edges are (src, dst) pairs treated as undirected springs.
    A final pass pushes apart vertices closer than min_distance, as far as the area allows.
    Return {vertex: (x, y)} with every point inside the margins.
    """
    vertices = list(vertices)
    if not vertices:
        return {}
    rng = rng or random.Random()
    inner_w, inner_h = max(width - 2 * margin, 1), max(height - 2 * margin, 1)
    k = 0.75 * math.sqrt(inner_w * inner_h / len(vertices))
    # Starting on an ellipse (with jitter) untangles much better than uniform random points.
    pos = {}
    for i, v in enumerate(vertices):
        angle = 2 * math.pi * i / len(vertices) + rng.uniform(-0.2, 0.2)
        pos[v] = [width / 2 + inner_w / 3 * math.cos(angle), height / 2 + inner_h / 3 * math.sin(angle)]
    start_temperature = max(inner_w, inner_h) / 10

    def direction(p, q):
        dx, dy = p[0] - q[0], p[1] - q[1]
        d = math.hypot(dx, dy)
        if d == 0:
            dx, dy = rng.uniform(-1, 1), rng.uniform(-1, 1)
            d = math.hypot(dx, dy) or 1.0
        return dx / d, dy / d, max(d, 0.01)

    for step in range(iterations):
        disp = {v: [0.0, 0.0] for v in vertices}
        for i, v in enumerate(vertices):
            for u in vertices[i + 1:]:
                dx, dy, d = direction(pos[v], pos[u])
                force = k * k / d
                disp[v][0] += dx * force
                disp[v][1] += dy * force
                disp[u][0] -= dx * force
                disp[u][1] -= dy * force
        for s, t in edges:
            dx, dy, d = direction(pos[s], pos[t])
            force = d * d / k
            disp[s][0] -= dx * force
            disp[s][1] -= dy * force
            disp[t][0] += dx * force
            disp[t][1] += dy * force

        temperature = start_temperature * (1 - step / iterations)
        for v in vertices:
            dx, dy = disp[v]
            d = math.hypot(dx, dy)
            if d > 0:
                move = min(d, temperature)
                pos[v][0] = min(max(pos[v][0] + dx / d * move, margin), width - margin)
                pos[v][1] = min(max(pos[v][1] + dy / d * move, margin), height - margin)

    for _ in range(100):
        moved = False
        for i, v in enumerate(vertices):
            for u in vertices[i + 1:]:
                dx, dy, d = direction(pos[v], pos[u])
                if d < min_distance:
                    push = (min_distance - d) / 2
                    for point, sign in ((pos[v], 1), (pos[u], -1)):
                        point[0] = min(max(point[0] + sign * dx * push, margin), width - margin)
                        point[1] = min(max(point[1] + sign * dy * push, margin), height - margin)
                    moved = True
        if not moved:
            break

    return {v: (x, y) for v, (x, y) in pos.items()}
