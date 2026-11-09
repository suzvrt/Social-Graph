"""Canvas drawing of a single vertex."""

import itertools

from socialgraph.config import FONT_FAMILY, MAX_NAME_LEN, NODE_RADIUS

_ids = itertools.count()


def _display_name(name):
    """Shorten long names (possible in imported files) so they fit inside the circle."""
    return name if len(name) <= MAX_NAME_LEN else name[:MAX_NAME_LEN - 1] + "…"


class NodeView:
    """A circle with the vertex name centered on it.

    Both canvas items share a unique tag, so moving, binding or deleting the tag
    affects the whole node.
    """

    def __init__(self, canvas, name, x, y, theme):
        self.canvas = canvas
        self.name = name
        self.x, self.y = x, y
        self.tag = "node_%d" % next(_ids)
        r = NODE_RADIUS
        self.circle = canvas.create_oval(x - r, y - r, x + r, y + r, width=1.5, tags=self.tag,
                                         fill=theme.node_fill, outline=theme.node_outline)
        self.label = canvas.create_text(x, y, text=_display_name(name), tags=self.tag, fill=theme.node_text,
                                        font=(FONT_FAMILY, 9, "bold"))

    def bind(self, sequence, callback):
        self.canvas.tag_bind(self.tag, sequence, callback)

    def move_to(self, x, y):
        self.canvas.move(self.tag, x - self.x, y - self.y)
        self.x, self.y = x, y

    def set_colors(self, fill, outline):
        self.canvas.itemconfigure(self.circle, fill=fill, outline=outline)

    def set_outline(self, outline):
        self.canvas.itemconfigure(self.circle, outline=outline)

    def set_text_color(self, color):
        self.canvas.itemconfigure(self.label, fill=color)

    def delete(self):
        self.canvas.delete(self.tag)
