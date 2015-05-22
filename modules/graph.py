#!C:\Python27
# -*- coding: utf-8 -*-

"""
graph

Build a graph that can be used by the dijkstra module.
"""

from __future__ import unicode_literals
import shapefile
from dijkstra import dijkstra


class Graph(dict):

    """Represents a graph (nodes with weighted links between them).

    It is built from a list of links taken from excel file. Is a subclass of
    a python dictionary where keys are all nodes of a network and values are
    lists of tuples (node_b, weight) representing the weighted links a
    particular node has.

    The representation of a network would be like this:

        {'a': [('b', 2), ('c', 3)],
         'b': [('a', 2), ('d', 5), ('e', 2)],
         'c': [('a', 3), ('e', 5)],
         'd': [('b', 5), ('e', 1), ('z', 2)],
         'e': [('b', 2), ('c', 5), ('d', 1), ('z', 4)],
         'z': [('d', 2), ('e', 4)]}
    """

    def add_edge(self, node_a, node_b, weight):
        """Add a node a to the graph with a weighted link with node b."""

        # create weighted link as a tuple
        weighted_edge = (node_b, float(weight))

        # create node_a if not already in graph
        if node_a not in self:
            self[node_a] = []

        # add link to node_a if not already present
        if weighted_edge not in self[node_a]:
            self[node_a].append(weighted_edge)

    def find_shortest_path(self, node_a, node_b):
        """Find shortest path between a and b nodes."""
        distance, path = dijkstra(self, node_a, node_b)
        return distance, path


def build_amtrak_rail_graph():
    graph = Graph()

    sf_lines = shapefile.Reader("rail/rail_lines")
    for record in sf_lines.iterRecords():
        from_id, to_id, miles = record[23], record[24], record[1]
        graph.add_edge(from_id, to_id, miles)
        graph.add_edge(to_id, from_id, miles)

    return graph


def get_amtrak_rail_graph():
    """
    TODO: should save graph when build to retrieve it when already built.
    """
    return build_amtrak_rail_graph()
