"""Read and write graphs in the SocialGraph text command format.

Each non-blank line is a command:
    add <src> <dst> <weight>   create the edge src -> dst (and its vertices)
    addv <name>                create an isolated vertex
    remove <name>              delete a vertex and its edges
Query commands from the original CLI (showFriends, shortestPath, recommendFriends)
are accepted and ignored, since they do not change the graph.
"""

import locale

from socialgraph.model.digraph import DiGraph

_QUERY_COMMANDS = {"showFriends", "shortestPath", "recommendFriends"}


class GraphFileError(ValueError):
    """A graph file line could not be interpreted."""


def parse_graph(lines):
    """Build a DiGraph by executing each command line in order."""
    graph = DiGraph()
    for number, line in enumerate(lines, start=1):
        parts = line.split()
        if not parts or parts[0] in _QUERY_COMMANDS:
            continue
        command, args = parts[0], parts[1:]
        if command == "add" and len(args) == 3:
            try:
                weight = int(args[2])
            except ValueError:
                weight = 0
            if weight <= 0:
                raise GraphFileError("Peso inválido na linha %d: %r" % (number, args[2]))
            graph.add_edge(args[0], args[1], weight)
        elif command == "addv" and len(args) == 1:
            graph.add_vertex(args[0])
        elif command == "remove" and len(args) == 1:
            graph.remove_vertex(args[0])
        else:
            raise GraphFileError("Comando inválido na linha %d: %r" % (number, line.strip()))
    return graph


def load_graph(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return parse_graph(file)
    except UnicodeDecodeError:
        # Files exported by v1 used the platform's default encoding (cp1252 on Windows).
        with open(path, "r", encoding=locale.getpreferredencoding(False)) as file:
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
