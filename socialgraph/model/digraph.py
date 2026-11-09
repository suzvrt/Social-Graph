"""Directed weighted graph used as the data model of SocialGraph.

@author: Enzo Suzart Pinto
"""


class Edge:
    """A weighted link to a target vertex, as stored in an adjacency set."""

    def __init__(self, vertex, cost):
        self.vertex = vertex
        self.cost = cost

    def __hash__(self):
        return hash((self.vertex, self.cost))

    def __eq__(self, other):
        return isinstance(other, Edge) and (self.vertex, self.cost) == (other.vertex, other.cost)

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        return "<%s, %s>" % (self.vertex, self.cost)


class DiGraph:
    """Directed graph mapping each vertex to the set of its outgoing edges."""

    def __init__(self):
        self._adj = {}

    def has_vertex(self, vertex):
        return vertex in self._adj

    def get_edge(self, src, dst):
        """Return the edge from src to dst, or None if it does not exist."""
        if self.has_vertex(src) and self.has_vertex(dst):
            for edge in self._adj[src]:
                if edge.vertex == dst:
                    return edge
        return None

    def has_edge(self, src, dst):
        if self.has_vertex(src) and self.has_vertex(dst):
            if self.get_edge(src, dst) is not None:
                return True
        else:
            return False

    def add_vertex(self, vertex):
        """Add an isolated vertex. Return False if it is None or already present."""
        if vertex is not None and not self.has_vertex(vertex):
            self._adj[vertex] = set()
            return True
        return False

    def add_edge(self, src, dst, cost=1):
        """Add src -> dst (creating missing vertices) or update its cost if it already exists."""
        if src == dst or src is None or dst is None or cost <= 0:
            return False
        self.add_vertex(src)
        self.add_vertex(dst)
        if not self.has_edge(src, dst):
            self._adj[src].add(Edge(dst, cost))
        else:
            for edge in self._adj[src]:
                if edge.vertex == dst:
                    edge.cost = cost
        return True

    def remove_vertex(self, vertex):
        """Remove a vertex and the edges pointing to it."""
        if self.has_vertex(vertex):
            self._adj.pop(vertex)
            for edges in self._adj.values():
                for edge in edges:
                    if vertex in edge.vertex:
                        edges.discard(edge)
                        break
            return True
        return False

    def num_vertices(self):
        return len(self._adj)

    def num_edges(self):
        return sum(len(edges) for edges in self._adj.values())

    def vertices(self):
        return list(self._adj)

    def edges(self):
        """Return every edge as a (src, cost, dst) tuple."""
        return [(src, edge.cost, edge.vertex) for src, edges in self._adj.items() for edge in edges]

    def adjacent_to(self, vertex):
        """Return the outgoing edges of a vertex."""
        if vertex is not None and self.has_vertex(vertex):
            # Rebuilt element by element so edges whose cost changed are re-hashed.
            return {edge for edge in self._adj[vertex]}
        return set()

    def incoming_edges(self, vertex):
        """Return edges pointing to vertex, each labelled with its source vertex."""
        incoming = set()
        if vertex is not None and self.has_vertex(vertex):
            for node in self._adj:
                if self.has_edge(node, vertex):
                    incoming.add(Edge(node, self.get_edge(node, vertex).cost))
        return incoming

    def dijkstra(self, source):
        """Single-source shortest paths.

        Return (distances, predecessors): a set of Edge(vertex, distance) for every reachable
        vertex and a dict mapping each vertex to the Edge of its predecessor on the path.
        """
        dist = set()
        predecessor = {}
        queue = self.vertices()

        for vertex in self.vertices():
            dist.add(Edge(vertex, float("inf")))
            predecessor[vertex] = None
        self._find(dist, source).cost = 0

        while queue:
            u = None
            for vertex in self._adj:
                if vertex in queue:
                    if u is None or self._find(dist, u).cost > self._find(dist, vertex).cost:
                        u = vertex
            if u is None:
                break
            queue.remove(u)
            for adjacent in self.adjacent_to(u):
                if adjacent.vertex in queue:
                    alt = self._find(dist, u).cost + adjacent.cost
                    if alt < self._find(dist, adjacent.vertex).cost:
                        # Remove before mutating: the cost is part of the Edge hash.
                        temp = self._find(dist, adjacent.vertex)
                        dist.remove(temp)
                        temp.cost = alt
                        dist.add(temp)
                        predecessor[adjacent.vertex] = self._find(dist, u)

        reachable = {edge for edge in dist if edge.cost != float("inf")}
        return reachable, predecessor

    def shortest_path(self, source, dest):
        """Return the vertices on the cheapest path from source to dest, or [] if unreachable."""
        path = []
        if source is not None and dest is not None and self.has_vertex(source) and self.has_vertex(dest):
            shortest, predecessor = self.dijkstra(source)
            target = self._find(shortest, dest)
            if target is not None and target.cost < float("inf"):
                current = dest
                while current != source:
                    path.insert(0, predecessor[current].vertex)
                    current = predecessor[current].vertex
                path.append(dest)
        return path

    @staticmethod
    def _find(edge_set, vertex):
        for edge in edge_set:
            if edge.vertex == vertex:
                return edge
        return None

    def __repr__(self):
        return "Vertices: %s\nEdges: %s" % (self.vertices(), " ".join(str(e) for e in self.edges()))
