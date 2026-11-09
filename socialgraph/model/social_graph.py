"""Friend recommendations computed over a DiGraph.

@author: Enzo Suzart Pinto
"""

BY_DISTANCE = "dist"
BY_WEIGHTED_DISTANCE = "weightedDist"


def recommend_friends(graph, person, option, top_k):
    """Recommend the top_k closest people who are not yet friends of person.

    Ties with the last recommendation are kept, so the result may exceed top_k.
    With BY_WEIGHTED_DISTANCE, each distance is multiplied by how few incoming edges
    (followers) the candidate has, favouring popular people.
    """
    if option == BY_DISTANCE:
        recommended = []
        for edge in graph.dijkstra(person)[0]:
            if edge not in graph.adjacent_to(person) and edge.vertex != person:
                recommended.append(edge)
        recommended.sort(key=lambda e: e.cost)
        candidates = recommended.copy()
        if len(recommended) > top_k:
            del recommended[top_k:]
        for edge in candidates:
            if edge not in recommended and edge.cost == recommended[-1].cost:
                recommended.append(edge)
        return recommended

    if option == BY_WEIGHTED_DISTANCE:
        recommended = recommend_friends(graph, person, BY_DISTANCE, top_k)
        for edge in recommended:
            edge.cost *= graph.num_edges() - len(graph.incoming_edges(edge.vertex))
        return recommended

    return None
