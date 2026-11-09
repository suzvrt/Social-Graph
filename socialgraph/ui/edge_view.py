"""Canvas drawing of a single directed edge."""

import itertools
import tkinter as tk

from socialgraph.config import FONT_FAMILY

_ids = itertools.count()


class EdgeView:
    """An arrow with its weight drawn on a small disc. Its path comes from a geometry.Route."""

    def __init__(self, canvas, cost, theme, route):
        self.canvas = canvas
        self.tag = "edge_%d" % next(_ids)
        self.line = canvas.create_line(0, 0, 0, 0, width=1.5, arrow=tk.LAST, capstyle=tk.ROUND, tags=self.tag,
                                       fill=theme.edge)
        self.label_bg = canvas.create_oval(0, 0, 0, 0, width=0, tags=self.tag, fill=theme.weight_bg)
        self.label = canvas.create_text(0, 0, text=cost, justify=tk.CENTER, tags=self.tag, fill=theme.weight_text,
                                        font=(FONT_FAMILY, 9, "bold"))
        self.redraw(route)
        # Edges stay below every node so arrows never hide vertex names.
        canvas.tag_lower(self.tag)

    def bind(self, sequence, callback):
        self.canvas.tag_bind(self.tag, sequence, callback)

    def redraw(self, route):
        self.route = route
        self.canvas.coords(self.line, *[c for point in route.points for c in point])
        self.canvas.itemconfigure(self.line, smooth=route.curved)
        self.canvas.coords(self.label, *route.label)
        x0, y0, x1, y1 = self.canvas.bbox(self.label)
        self.canvas.coords(self.label_bg, x0 - 0.5, y0, x1, y1)

    def set_cost(self, cost):
        self.canvas.itemconfigure(self.label, text=cost)
        self.redraw(self.route)

    def set_color(self, color):
        self.canvas.itemconfigure(self.line, fill=color)

    def apply_theme(self, theme):
        self.set_color(theme.edge)
        self.canvas.itemconfigure(self.label, fill=theme.weight_text)
        self.canvas.itemconfigure(self.label_bg, fill=theme.weight_bg)

    def delete(self):
        self.canvas.delete(self.tag)
