import unittest

from socialgraph.config import MAX_NAME_LEN
from socialgraph.model.names import name_error, normalize_name


class NameTests(unittest.TestCase):
    def test_normalize_trims_and_capitalizes(self):
        self.assertEqual(normalize_name("  aNA "), "Ana")

    def test_valid_name_has_no_error(self):
        self.assertIsNone(name_error("Ana"))

    def test_invalid_names_are_reported(self):
        for name in ("", "Ana2", "Ana Maria", "x" * (MAX_NAME_LEN + 1)):
            with self.subTest(name=name):
                self.assertIsNotNone(name_error(name))


if __name__ == "__main__":
    unittest.main()
