import os
import tempfile
import unittest
from pathlib import Path

from socialgraph.model import graph_io
from socialgraph.model.graph_io import GraphFileError

SAMPLE = Path(__file__).resolve().parent.parent / "infile.txt"


class ParseTests(unittest.TestCase):
    def test_sample_file_applies_add_and_remove_commands(self):
        graph = graph_io.load_graph(SAMPLE)
        self.assertFalse(graph.has_vertex("Jim"))
        self.assertEqual(graph.get_edge("James", "Larry").cost, 2)
        self.assertEqual(graph.num_edges(), 8)

    def test_blank_lines_are_skipped(self):
        graph = graph_io.parse_graph(["add A B 1", "", "   ", "addv C"])
        self.assertCountEqual(graph.vertices(), ["A", "B", "C"])

    def test_errors_report_the_line_number(self):
        cases = [
            ["addv A", "add A B"],
            ["addv A", "add A B heavy"],
            ["addv A", "add A B 0"],
            ["addv A", "connect A B 1"],
        ]
        for lines in cases:
            with self.subTest(lines=lines), self.assertRaisesRegex(GraphFileError, "linha 2"):
                graph_io.parse_graph(lines)


class LoadTests(unittest.TestCase):
    def test_utf8_file_with_accents(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "graph.txt")
            graph_io.save_graph(graph_io.parse_graph(["add José Ângela 2"]), path)
            self.assertTrue(graph_io.load_graph(path).has_edge("José", "Ângela"))


class SerializeTests(unittest.TestCase):
    def test_round_trip_preserves_vertices_and_edges(self):
        original = graph_io.parse_graph(["add A B 2", "add B A 3", "addv Lonely"])
        lines = graph_io.serialize_graph(original)
        self.assertIn("addv Lonely", lines)
        copy = graph_io.parse_graph(lines)
        self.assertCountEqual(copy.vertices(), original.vertices())
        self.assertCountEqual(copy.edges(), original.edges())


if __name__ == "__main__":
    unittest.main()
