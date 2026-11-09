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

# Random placement of a new vertex gives up after this many attempts to find a free spot.
MAX_PLACEMENT_TRIES = 25000

# Force-directed layout used when importing a file. More iterations settle better but import slower.
LAYOUT_ITERATIONS = 200

# Edge routing, in pixels: gap between the two arrows of A->B / B->A, minimum distance
# kept from other vertices, and the curve bends tried (in order) to get around them.
EDGE_PAIR_OFFSET = 8
EDGE_CLEARANCE = 6
EDGE_BENDS = (40, 80, 130, 200)
