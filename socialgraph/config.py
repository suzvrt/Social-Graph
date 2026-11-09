"""Application-wide constants and file locations."""

from pathlib import Path

APP_NAME = "SocialGraph"

PROJECT_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = PROJECT_DIR / "assets" / "icon.ico"

FONT_FAMILY = "Segoe UI"

NODE_RADIUS = 35
MAX_NAME_LEN = 10

MIN_WEIGHT = 1
MAX_WEIGHT = 5

PATH_HIGHLIGHT_MS = 4000

# Random placement gives up after this many attempts to find a free spot.
MAX_PLACEMENT_TRIES = 25000
