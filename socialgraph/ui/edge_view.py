"""Canvas drawing of a single directed edge."""

import itertools
import tkinter as tk

from socialgraph.config import FONT_FAMILY, NODE_RADIUS

_ids = itertools.count()


class EdgeView:
    """An arrow between two NodeViews with its weight drawn on a small disc at the midpoint."""

    def __init__(self, canvas, src, dst, cost, theme):
        self.canvas = canvas
        self.src = src
        self.dst = dst
        self.tag = "edge_%d" % next(_ids)
        self.line = canvas.create_line(0, 0, 0, 0, width=1.5, arrow=tk.LAST, capstyle=tk.ROUND, tags=self.tag,
                                       fill=theme.edge)
        self.label_bg = canvas.create_oval(0, 0, 0, 0, width=0, tags=self.tag, fill=theme.weight_bg)
        self.label = canvas.create_text(0, 0, text=cost, justify=tk.CENTER, tags=self.tag, fill=theme.weight_text,
                                        font=(FONT_FAMILY, 9, "bold"))
        self.redraw()
        # Edges stay below every node so arrows never hide vertex names.
        canvas.tag_lower(self.tag)

    def bind(self, sequence, callback):
        self.canvas.tag_bind(self.tag, sequence, callback)

    def redraw(self):
        """Recompute the arrow so it goes from border to border of the two circles."""
        dx, dy = self.dst.x - self.src.x, self.dst.y - self.src.y
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        ax, ay = self.src.x + NODE_RADIUS * ux, self.src.y + NODE_RADIUS * uy
        bx, by = self.dst.x - NODE_RADIUS * ux, self.dst.y - NODE_RADIUS * uy
        self.canvas.coords(self.line, ax, ay, bx, by)
        self.canvas.coords(self.label, (ax + bx) // 2, (ay + by) // 2)
        x0, y0, x1, y1 = self.canvas.bbox(self.label)
        self.canvas.coords(self.label_bg, x0 - 0.5, y0, x1, y1)

    def set_cost(self, cost):
        self.canvas.itemconfigure(self.label, text=cost)
        self.redraw()

    def set_color(self, color):
        self.canvas.itemconfigure(self.line, fill=color)

    def delete(self):
        self.canvas.delete(self.tag)
