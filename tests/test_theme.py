import dataclasses
import os
import tempfile
import unittest

from socialgraph.settings import load_settings, save_settings
from socialgraph.theme import DARK, THEMES, get_theme


class ThemeTests(unittest.TestCase):
    def test_lookup_falls_back_to_dark(self):
        self.assertIs(get_theme("light"), THEMES["light"])
        self.assertIs(get_theme("neon"), DARK)

    def test_every_theme_defines_valid_colors(self):
        for theme in THEMES.values():
            for field in dataclasses.fields(theme):
                if field.name not in ("key", "name"):
                    with self.subTest(theme=theme.key, field=field.name):
                        self.assertRegex(getattr(theme, field.name), r"^#[0-9a-f]{6}$")


class SettingsTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "settings.json")
            save_settings({"theme": "light"}, path)
            self.assertEqual(load_settings(path), {"theme": "light"})

    def test_missing_or_corrupt_file_gives_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "settings.json")
            self.assertEqual(load_settings(path), {})
            with open(path, "w", encoding="utf-8") as file:
                file.write("{not json")
            self.assertEqual(load_settings(path), {})


if __name__ == "__main__":
    unittest.main()
