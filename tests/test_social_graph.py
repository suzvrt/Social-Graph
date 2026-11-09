import unittest
from pathlib import Path

from socialgraph.model import graph_io
from socialgraph.model.digraph import DiGraph, Edge
from socialgraph.model.social_graph import BY_DISTANCE, BY_WEIGHTED_DISTANCE, recommend_friends

SAMPLE = Path(__file__).resolve().parent.parent / "infile.txt"


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.graph = graph_io.load_graph(SAMPLE)

    def test_by_distance_keeps_ties_with_the_last_candidate(self):
        result = recommend_friends(self.graph, "James", BY_DISTANCE, 2)
        self.assertEqual(result, [Edge("Keith", 2), Edge("Kaith", 3), Edge("Paul", 3)])

    def test_by_weighted_distance_favours_people_with_more_followers(self):
        result = recommend_friends(self.graph, "James", BY_WEIGHTED_DISTANCE, 5)
        self.assertEqual(result, [Edge("Keith", 14), Edge("Kaith", 15), Edge("Paul", 21), Edge("Pie", 35)])

    def test_direct_friends_are_never_recommended(self):
        graph = DiGraph()
        graph.add_edge("A", "B", 5)
        graph.add_edge("A", "C", 1)
        graph.add_edge("C", "B", 1)
        graph.add_edge("C", "D", 1)
        result = recommend_friends(graph, "A", BY_DISTANCE, 5)
        self.assertEqual([edge.vertex for edge in result], ["D"])

    def test_no_candidates_returns_empty_list(self):
        graph = DiGraph()
        graph.add_edge("A", "B", 1)
        self.assertEqual(recommend_friends(graph, "A", BY_DISTANCE, 3), [])
        self.assertEqual(recommend_friends(graph, "A", BY_WEIGHTED_DISTANCE, 3), [])

    def test_unknown_person_or_non_positive_top_k_returns_empty_list(self):
        self.assertEqual(recommend_friends(self.graph, "Ghost", BY_DISTANCE, 3), [])
        self.assertEqual(recommend_friends(self.graph, "James", BY_DISTANCE, 0), [])

    def test_unknown_option_raises(self):
        with self.assertRaises(ValueError):
            recommend_friends(self.graph, "James", "popularity", 3)


if __name__ == "__main__":
    unittest.main()
