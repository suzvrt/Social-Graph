import unittest

from socialgraph.model.digraph import DiGraph, Edge


class VertexTests(unittest.TestCase):
    def test_add_vertex_rejects_duplicates_and_none(self):
        graph = DiGraph()
        self.assertTrue(graph.add_vertex("Ana"))
        self.assertFalse(graph.add_vertex("Ana"))
        self.assertFalse(graph.add_vertex(None))
        self.assertEqual(graph.vertices(), ["Ana"])

    def test_remove_vertex_drops_its_incoming_and_outgoing_edges(self):
        graph = DiGraph()
        graph.add_edge("A", "B", 1)
        graph.add_edge("C", "B", 2)
        graph.add_edge("B", "D", 3)
        self.assertTrue(graph.remove_vertex("B"))
        self.assertEqual(graph.num_edges(), 0)
        self.assertCountEqual(graph.vertices(), ["A", "C", "D"])

    def test_remove_vertex_matches_names_exactly(self):
        graph = DiGraph()
        graph.add_edge("X", "Anabela", 1)
        graph.add_edge("X", "Ana", 2)
        graph.remove_vertex("Ana")
        self.assertEqual(graph.adjacent_to("X"), {Edge("Anabela", 1)})

    def test_remove_missing_vertex_returns_false(self):
        self.assertFalse(DiGraph().remove_vertex("Ghost"))


class EdgeTests(unittest.TestCase):
    def test_add_edge_creates_missing_vertices(self):
        graph = DiGraph()
        self.assertTrue(graph.add_edge("A", "B", 3))
        self.assertCountEqual(graph.vertices(), ["A", "B"])
        self.assertEqual(graph.get_edge("A", "B"), Edge("B", 3))
        self.assertIsNone(graph.get_edge("B", "A"))

    def test_add_edge_rejects_invalid_input(self):
        graph = DiGraph()
        self.assertFalse(graph.add_edge("A", "A", 1))
        self.assertFalse(graph.add_edge("A", None, 1))
        self.assertFalse(graph.add_edge("A", "B", 0))
        self.assertEqual(graph.num_vertices(), 0)

    def test_add_existing_edge_updates_its_cost(self):
        graph = DiGraph()
        graph.add_edge("A", "B", 1)
        graph.add_edge("A", "B", 2)
        self.assertEqual(graph.num_edges(), 1)
        self.assertIn(Edge("B", 2), graph.adjacent_to("A"))
        self.assertIn(Edge("A", 2), graph.incoming_edges("B"))

    def test_has_edge_is_always_a_bool(self):
        graph = DiGraph()
        graph.add_edge("A", "B", 1)
        self.assertIs(graph.has_edge("A", "B"), True)
        self.assertIs(graph.has_edge("B", "A"), False)
        self.assertIs(graph.has_edge("A", "Ghost"), False)

    def test_edges_lists_src_cost_dst(self):
        graph = DiGraph()
        graph.add_edge("A", "B", 1)
        graph.add_edge("B", "A", 4)
        self.assertCountEqual(graph.edges(), [("A", 1, "B"), ("B", 4, "A")])


class ShortestPathTests(unittest.TestCase):
    def setUp(self):
        self.graph = DiGraph()
        self.graph.add_edge("A", "B", 5)
        self.graph.add_edge("A", "C", 1)
        self.graph.add_edge("C", "B", 1)
        self.graph.add_vertex("Isolated")

    def test_prefers_cheaper_indirect_path(self):
        self.assertEqual(self.graph.shortest_path("A", "B"), ["A", "C", "B"])

    def test_dijkstra_returns_only_reachable_vertices(self):
        distances, _ = self.graph.dijkstra("A")
        self.assertEqual(distances, {"A": 0, "C": 1, "B": 2})

    def test_unreachable_or_missing_vertex_gives_empty_path(self):
        self.assertEqual(self.graph.shortest_path("B", "A"), [])
        self.assertEqual(self.graph.shortest_path("A", "Isolated"), [])
        self.assertEqual(self.graph.shortest_path("A", "Ghost"), [])


if __name__ == "__main__":
    unittest.main()
