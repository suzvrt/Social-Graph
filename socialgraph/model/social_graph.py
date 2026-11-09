"""Friend recommendations computed over a DiGraph.

@author: Enzo Suzart Pinto
"""

from socialgraph.model.digraph import Edge

BY_DISTANCE = "dist"
BY_WEIGHTED_DISTANCE = "weightedDist"


def recommend_friends(graph, person, option, top_k):
    """Recommend the top_k closest people that person does not follow yet.

    Return a list of Edge(candidate, score), best (lowest score) first. Candidates
    tied with the last one are kept, so the result may exceed top_k.

    BY_DISTANCE scores by shortest-path distance. BY_WEIGHTED_DISTANCE takes the same
    candidates and multiplies each distance by (total edges - candidate's followers),
    favouring popular people.
    """
    if option not in (BY_DISTANCE, BY_WEIGHTED_DISTANCE):
        raise ValueError("Unknown recommendation option: %r" % option)
    if not graph.has_vertex(person) or top_k < 1:
        return []

    distances, _ = graph.dijkstra(person)
    friends = {edge.vertex for edge in graph.adjacent_to(person)}
    candidates = sorted((Edge(vertex, dist) for vertex, dist in distances.items()
                         if vertex != person and vertex not in friends),
                        key=lambda e: (e.cost, e.vertex))
    if len(candidates) > top_k:
        cutoff = candidates[top_k - 1].cost
        candidates = [edge for edge in candidates if edge.cost <= cutoff]

    if option == BY_WEIGHTED_DISTANCE:
        total = graph.num_edges()
        candidates = sorted((Edge(e.vertex, e.cost * (total - len(graph.incoming_edges(e.vertex))))
                             for e in candidates),
                            key=lambda e: (e.cost, e.vertex))
    return candidates
