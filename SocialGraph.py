"""@package SocialGraph
Module created to create a Social Graph from a file
@author: Enzo Suzart Pinto
@date: 02/09/2019
"""

import DiGraph
import sys


class SocialGraph(object):
    def __init__(self, file):
        """Constructor from a ﬁle of commands."""
        self.file = file
        self.dg = DiGraph.DiGraph()
        self.readGraphFile(file)

    def readGraphFile(self, file):
        """Create a graph from a file."""
        with open(file, 'r') as f:
            for line in f:
                line = line.split()
                if line[0] == 'add':
                    s = "addEdge: ("
                    s += str(self.dg.addEdge(line[1], line[2], int(line[3]))) + ") - "
                    s += str(self.dg.numEdges()) + " edges, "
                    s += str(self.dg.numVertices()) + " vertices\n"
                if line[0] == 'showFriends':
                    s = str(self.dg.adjacentTo(line[1]))
                if line[0] == 'remove':
                    s = "remove: ("
                    s += str(self.dg.removeVertex(line[1])) + ") - "
                    s += str(self.dg.numEdges()) + " edges, "
                    s += str(self.dg.numVertices()) + " vertices\n"
                if line[0] == 'shortestPath':
                    s = str(self.dg.Dijkstra2(line[1], line[2]))
                if line[0] == 'recommendFriends':
                    s = str(self.recommendFriends(line[1], line[2], int(line[3]), self.dg))
                if line[0] == 'addv':
                    self.dg.addVertex(line[1])

    def recommendFriends(self, personOfInterest, option, topK, dg):
        """Recommend topK (e.g., 5) best friend candidates who are not already a friend of personOfInterest."""
        if option == 'dist':
            recommended = []
            for edge in dg.Dijkstra(personOfInterest)[0]:
                if edge not in dg.adjacentTo(personOfInterest) and edge.getVertex() != personOfInterest:
                    recommended.append(edge)
            recommended.sort(reverse=False, key=lambda x: x.getCost())
            check = recommended.copy()
            if len(recommended) > topK:
                while len(recommended) != topK:
                    recommended.pop(-1)
            for edge in check:
                if edge not in recommended:
                    if edge.getCost() == recommended[-1].getCost():
                        recommended.append(edge)
            return recommended
        if option == 'weightedDist':
            recommended = self.recommendFriends(personOfInterest, 'dist', topK, dg)
            for person in recommended:
                cost = dg.numEdges() - len(dg.incomingEdges(person.getVertex()))
                cost = cost * person.getCost()
                person.setCost(cost)
            return recommended


def main():
    if len(sys.argv) < 2:
        raise Exception("Filename cannot be empty!")
    file = sys.argv[1]
    sc = SocialGraph(file)


if __name__ == '__main__':
    main()
