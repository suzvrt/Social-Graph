"""Read and write graphs in the SocialGraph text command format.

Each line is a command:
    add <src> <dst> <weight>   create the edge src -> dst (and its vertices)
    addv <name>                create an isolated vertex
    remove <name>              delete a vertex and its edges
Query commands from the original CLI (showFriends, shortestPath, recommendFriends)
are accepted and ignored, since they do not change the graph.
"""

from socialgraph.model.digraph import DiGraph


def parse_graph(lines):
    """Build a DiGraph by executing each command line in order."""
    graph = DiGraph()
    for line in lines:
        parts = line.split()
        if parts[0] == "add":
            graph.add_edge(parts[1], parts[2], int(parts[3]))
        elif parts[0] == "addv":
            graph.add_vertex(parts[1])
        elif parts[0] == "remove":
            graph.remove_vertex(parts[1])
    return graph


def load_graph(path):
    with open(path, "r", encoding="utf-8") as file:
        return parse_graph(file)


def serialize_graph(graph):
    """Return the command lines that rebuild graph: edges first, then isolated vertices."""
    lines = ["add %s %s %s" % (src, dst, cost) for src, cost, dst in graph.edges()]
    for vertex in graph.vertices():
        if not graph.adjacent_to(vertex) and not graph.incoming_edges(vertex):
            lines.append("addv %s" % vertex)
    return lines


def save_graph(graph, path):
    with open(path, "w", encoding="utf-8") as file:
        file.writelines(line + "\n" for line in serialize_graph(graph))
