"""Color palettes used to draw the graph."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Every color the canvas uses. Widgets must read colors from here, never hardcode them."""

    name: str
    canvas_bg: str
    node_fill: str
    node_outline: str
    node_text: str
    source_fill: str
    source_outline: str
    target_fill: str
    target_outline: str
    edge: str
    weight_text: str
    weight_bg: str
    path_highlight: str


DARK = Theme(
    name="Escuro",
    canvas_bg="#2b2b2b",
    node_fill="#2b2b2b",
    node_outline="#cc7832",
    node_text="#a9b7c6",
    source_fill="#3b514d",
    source_outline="#e0ee27",
    target_fill="#2a2a5a",
    target_outline="#b200b2",
    edge="#ffc66d",
    weight_text="#94558d",
    weight_bg="#2b2b2b",
    path_highlight="#5c96ba",
)
