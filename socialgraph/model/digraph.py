"""Directed weighted graph used as the data model of SocialGraph.

@author: Enzo Suzart Pinto
"""

import heapq
from typing import NamedTuple


class Edge(NamedTuple):
    """A weighted link to `vertex`. Immutable, so it is safe to keep in sets."""

    vertex: str
    cost: float

    def __repr__(self):
        return "<%s, %s>" % (self.vertex, self.cost)


class DiGraph:
    """Directed graph stored as an adjacency map: {src: {dst: cost}}."""

    def __init__(self):
        self._adj = {}

    def has_vertex(self, vertex):
        return vertex in self._adj

    def has_edge(self, src, dst):
        return dst in self._adj.get(src, {})

    def get_edge(self, src, dst):
        """Return the edge from src to dst, or None if it does not exist."""
        cost = self._adj.get(src, {}).get(dst)
        return None if cost is None else Edge(dst, cost)

    def add_vertex(self, vertex):
        """Add an isolated vertex. Return False if it is None or already present."""
        if vertex is None or self.has_vertex(vertex):
            return False
        self._adj[vertex] = {}
        return True

    def add_edge(self, src, dst, cost=1):
        """Add src -> dst (creating missing vertices) or update its cost if it already exists."""
        if src == dst or src is None or dst is None or cost <= 0:
            return False
        self.add_vertex(src)
        self.add_vertex(dst)
        self._adj[src][dst] = cost
        return True

    def remove_vertex(self, vertex):
        """Remove a vertex together with its outgoing and incoming edges."""
        if not self.has_vertex(vertex):
            return False
        del self._adj[vertex]
        for targets in self._adj.values():
            targets.pop(vertex, None)
        return True

    def num_vertices(self):
        return len(self._adj)

    def num_edges(self):
        return sum(len(targets) for targets in self._adj.values())

    def vertices(self):
        return list(self._adj)

    def edges(self):
        """Return every edge as a (src, cost, dst) tuple."""
        return [(src, cost, dst) for src, targets in self._adj.items() for dst, cost in targets.items()]

    def adjacent_to(self, vertex):
        """Return the outgoing edges of a vertex."""
        return {Edge(dst, cost) for dst, cost in self._adj.get(vertex, {}).items()}

    def incoming_edges(self, vertex):
        """Return edges pointing to vertex, each labelled with its source vertex."""
        return {Edge(src, targets[vertex]) for src, targets in self._adj.items() if vertex in targets}

    def dijkstra(self, source):
        """Single-source shortest paths.

        Return (distances, predecessors) as dicts keyed by vertex, containing only
        vertices reachable from source. Both are empty if source is not in the graph.
        """
        if not self.has_vertex(source):
            return {}, {}
        distances = {source: 0}
        predecessors = {}
        visited = set()
        heap = [(0, source)]
        while heap:
            dist, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            for v, cost in self._adj[u].items():
                alt = dist + cost
                if v not in distances or alt < distances[v]:
                    distances[v] = alt
                    predecessors[v] = u
                    heapq.heappush(heap, (alt, v))
        return distances, predecessors

    def shortest_path(self, source, dest):
        """Return the vertices on the cheapest path from source to dest, or [] if unreachable."""
        distances, predecessors = self.dijkstra(source)
        if dest not in distances:
            return []
        path = [dest]
        while path[0] != source:
            path.insert(0, predecessors[path[0]])
        return path

    def __repr__(self):
        return "Vertices: %s\nEdges: %s" % (self.vertices(), " ".join(str(e) for e in self.edges()))
