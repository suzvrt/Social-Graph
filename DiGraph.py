"""@package DiGraph
Module created to manipulate a directed graph
@author: Enzo Suzart Pinto
@date: 02/09/2019
"""


def cmp(x, y):
    return (x > y) - (x < y)


class DiGraph(object):
    def __init__(self):
        """Creates an empty graph."""
        self.graph = {}

    def hasVertex(self, vertex):
        """Checks whether a given vertex is in the graph."""
        if vertex in self.graph.keys():
            return True
        else:
            return False

    def getEdge(self, src, dst):
        """Gets the edge from src to dst, if such an edge exists."""
        if self.hasVertex(src) and self.hasVertex(dst):
            for edge in self.graph[src]:
                if edge.getVertex() == dst:
                    return edge
        return None

    def hasEdge(self, src, dst):
        """Check whether an edge from src to dst exists."""
        if self.hasVertex(src) and self.hasVertex(dst):
            if self.getEdge(src, dst) is not None:
                return True
        else:
            return False

    def addVertex(self, vertex):
        """Add a vertex to the graph with an empty set of edges associated with it."""
        if vertex is not None and not self.hasVertex(vertex):
            self.graph[vertex] = set()
            return True
        else:
            return False

    def addEdge(self, src, dst, c=1):
        """Add a directed edge from the source node to the destination node."""
        if src == dst or src is None or dst is None or c <= 0:
            return False
        else:
            if not self.hasVertex(src):
                self.addVertex(src)
            if not self.hasVertex(dst):
                self.addVertex(dst)
            if not self.hasEdge(src, dst):
                self.graph[src].add(Edge(dst, c))
                return True
            else:
                for edge in self.graph[src]:
                    if edge.getVertex() == dst:
                        edge.setCost(c)
                return True

    def numVertices(self):
        """Returns the number of vertices in this graph."""
        return len(self.graph.keys())

    def vertices(self):
        """Returns all vertices in this graph."""
        __vertex = []
        for node in self.graph.keys():
            __vertex.append(node)
        return __vertex

    def edges(self):
        """Returns all edges in this graph."""
        return self.__generate_edges()

    def adjacentTo(self, vertex):
        """Gets all vertices adjacent to a given vertex."""
        __adjacent = set()
        if vertex is not None and self.hasVertex(vertex) and self.graph[vertex] != set():
            for edge in self.graph[vertex]:
                __adjacent.add(edge)
        return __adjacent

    def numEdges(self):
        """Returns the number of edges in this graph."""
        __numEdges = 0
        for edges in self.graph.values():
            __numEdges += len(edges)
        return __numEdges

    def removeVertex(self, vertex):
        """Remove this vertex from the graph if possible and
         calculate the number of edges in the graph accordingly.
        """
        if self.hasVertex(vertex):
            self.graph.pop(vertex)
            for node, edges in self.graph.items():
                for edge in edges:
                    if vertex in edge.getVertex():
                        edges.discard(edge)
                        break
            return True
        return False

    def incomingEdges(self, vertex):
        """Return a set of nodes with edges coming to this given vertex."""
        __incoming = set()
        if vertex is not None and self.hasVertex(vertex):
            for node, edges in self.graph.items():
                if self.hasEdge(node, vertex):
                    __incoming.add(Edge(node, self.getEdge(node, vertex).getCost()))
        return __incoming

    def __generate_edges(self):
        """A method generating the edges of the graph."""
        gen = []
        for node, edges in self.graph.items():
            for edge in edges:
                if (edge.getVertex(), node) not in gen:
                    gen.append((node, edge.getCost(), edge.getVertex()))
        return gen

    def getInfinity(self):
        """Returns the largest edge cost."""
        __infinity = 0
        for node, edges in self.graph.items():
            for edge in edges:
                if edge.getCost() > __infinity:
                    __infinity = edge.getCost()
        return __infinity

    def Dijkstra(self, source):
        """Compute Dijkstra single source shortest path from the source node.
        Python algorithm adapted from: https://en.wikipedia.org/wiki/Dijkstra's_algorithm#Pseudocode
        """
        __dist = set()
        __pathToNode = {}
        Q = self.vertices()

        for vertex in self.vertices():
            __dist.add(Edge(vertex, float('inf')))
            __pathToNode[vertex] = None
        self.__getFromEdgeSet(__dist, source).setCost(0)

        while Q:
            u = None
            for vertex, edges in self.graph.items():
                if vertex in Q:
                    if u is None:
                        u = vertex
                    elif Edge.cmpCost(self.__getFromEdgeSet(__dist, u), self.__getFromEdgeSet(__dist, vertex)) == 1:
                        u = vertex
            if u is None:
                break
            Q.remove(u)
            for adjacent in self.adjacentTo(u):
                if adjacent.getVertex() in Q and self.getEdge(u, adjacent.getVertex()) is not None:
                    alt = self.__getFromEdgeSet(__dist, u).getCost() + self.getEdge(u, adjacent.getVertex()).getCost()
                    if alt < self.__getFromEdgeSet(__dist, adjacent.getVertex()).getCost():
                        temp = self.__getFromEdgeSet(__dist, adjacent.getVertex())
                        __dist.remove(temp)
                        temp.setCost(alt)
                        __dist.add(temp)
                        __pathToNode[adjacent.getVertex()] = self.__getFromEdgeSet(__dist, u)

        __dist2 = __dist.copy()
        for edge in __dist:
            if edge.getCost() == float('inf'):
                __dist2.remove(edge)
        __dist = __dist2.copy()
        return __dist, __pathToNode

    def Dijkstra2(self, source, dest):
        """Compute Dijkstra shortest path from the source to the destination node"""
        __pathToNode = []
        if source is not None and dest is not None and self.hasVertex(source) and self.hasVertex(dest):
            shortest, __predecessor = self.Dijkstra(source)
            if self.__getFromEdgeSet(shortest, dest) is not None:
                if self.__getFromEdgeSet(shortest, dest).getCost() < float('inf'):
                    currentNode = dest
                    while currentNode != source:
                        __pathToNode.insert(0, __predecessor[currentNode])
                        if isinstance(currentNode, str):
                            currentNode = __predecessor[currentNode].getVertex()
                        if isinstance(currentNode, Edge):
                            currentNode = __predecessor[currentNode.getVertex()].getVertex()
                    __pathToNode.append(self.__getFromEdgeSet(shortest, dest))
        return __pathToNode

    @staticmethod
    def __getFromEdgeSet(edge_set, vertex):
        """Since sets are not indexed, this method returns the required edge
        that include the inserted vertex (if it exists, if not, it wil return None)
        """
        if edge_set != set():
            for edge in edge_set:
                if vertex == edge.getVertex():
                    return edge
        return None

    def __repr__(self):
        """Return a representation of the graph as a string."""
        res = "Vertices: %s" % (self.vertices())
        res += "\nEdges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return str(res)


class Edge(object):
    def __init__(self, n, c):
        """Constructor from a node and its cost."""
        self.n = n
        self.c = c

    def getVertex(self):
        """Get the target vertex."""
        return self.n

    def getCost(self):
        """Get this edge cost."""
        return self.c

    def setCost(self, c):
        """Set the cost of this edge."""
        self.c = c

    def cmpCost(self, other):
        """Compare two edges based on the cost only, not on the vertex."""
        return cmp(self.getCost(), other.getCost())

    def __repr__(self):
        """An unambiguous representation of this edge."""
        s = "<" + self.getVertex() + ", " + str(self.getCost()) + ">"
        return s

    def __str__(self):
        """String conversion of this edge."""
        s = "<" + self.getVertex() + ", " + str(self.getCost()) + ">"
        return s

    def __hash__(self):
        """An Edge object must be hashable."""
        return hash((self.n, self.c))

    def __eq__(self, obj):
        """Operator ==."""
        if isinstance(obj, Edge) and self.getVertex() == obj.getVertex() and self.getCost() == obj.getCost():
            return True
        else:
            return False

    def __contains__(self, obj):
        """Operator in."""
        if isinstance(obj, Edge) and self.getVertex() == obj.getVertex():
            return True
        else:
            return False

    def __lt__(self, obj):
        """Built-in comparator in 3.x"""
        return self.c < obj.c


def main(args=None):
    d = DiGraph()


if __name__ == "__main__":
    main()
