"""User preferences persisted as JSON in the home folder."""

import json

from socialgraph.config import SETTINGS_PATH


def load_settings(path=SETTINGS_PATH):
    """Return the saved preferences, or {} if the file is missing or unreadable."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings, path=SETTINGS_PATH):
    """Write preferences. Failing to save them must never break the app, so errors are ignored."""
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=2)
    except OSError:
        pass
