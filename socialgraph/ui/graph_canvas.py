"""Interactive canvas that keeps the drawing in sync with a DiGraph."""

import tkinter as tk
from random import randint
from tkinter import messagebox

from socialgraph.config import MAX_PLACEMENT_TRIES, NODE_RADIUS, PATH_HIGHLIGHT_MS
from socialgraph.model.digraph import DiGraph
from socialgraph.ui.dialogs import ask_weight
from socialgraph.ui.edge_view import EdgeView
from socialgraph.ui.node_view import NodeView


class PlacementError(Exception):
    """Raised when there is no free room left on the canvas for a new vertex."""


class GraphCanvas(tk.Canvas):
    """Owns the graph model and its views, and handles mouse interaction with them.

    Selection holds up to two vertex names: index 0 is the source (green) and
    index 1 the destination (purple) used by edge creation and shortest path.
    """

    def __init__(self, master, theme, on_change):
        super().__init__(master, bg=theme.canvas_bg, highlightthickness=0)
        self.theme = theme
        self.on_change = on_change
        self.graph = DiGraph()
        self.nodes = {}
        self.edges = {}
        self.selection = []

    def clear(self):
        self.graph = DiGraph()
        self.nodes.clear()
        self.edges.clear()
        self.selection.clear()
        self.delete("all")

    def load_graph(self, graph):
        """Replace the current drawing with graph, placing its vertices randomly."""
        self.clear()
        for vertex in graph.vertices():
            self.add_node(vertex)
        for src, cost, dst in graph.edges():
            self.add_edge(src, dst, cost)

    def add_node(self, name):
        if self.graph.has_vertex(name):
            return
        x, y = self._find_free_spot()
        self.graph.add_vertex(name)
        view = NodeView(self, name, x, y, self.theme)
        view.bind("<Button-3>", lambda e: self._show_node_menu(e, name))
        view.bind("<B1-Motion>", lambda e: self._drag_node(e, name))
        view.bind("<Control-1>", lambda e: self.toggle_selection(name))
        self.nodes[name] = view

    def add_edge(self, src, dst, cost):
        self.graph.add_edge(src, dst, cost)
        view = EdgeView(self, self.nodes[src], self.nodes[dst], cost, self.theme)
        view.bind("<Double-Button-1>", lambda e: self._change_weight(src, dst))
        self.edges[(src, dst)] = view

    def delete_node(self, name):
        self.graph.remove_vertex(name)
        for key in [key for key in self.edges if name in key]:
            self.edges.pop(key).delete()
        self.nodes.pop(name).delete()
        if name in self.selection:
            self.selection.remove(name)
            self._restyle_selection()

    def move_node(self, name, x, y):
        self.nodes[name].move_to(x, y)
        for (src, dst), view in self.edges.items():
            if name in (src, dst):
                view.redraw()

    def toggle_selection(self, name):
        """Ctrl+click: select a vertex, or unselect it if it was already selected.

        Selecting a third vertex drops the oldest one, so the previous destination
        becomes the new source.
        """
        if name in self.selection:
            self.selection.remove(name)
        else:
            self.selection.append(name)
            if len(self.selection) > 2:
                self.selection.pop(0)
        self._restyle_selection()

    def highlight_path(self, path):
        """Temporarily paint the edges and vertices of path."""
        for src, dst in zip(path, path[1:]):
            self.edges[(src, dst)].set_color(self.theme.path_highlight)
        for name in path:
            self.nodes[name].set_outline(self.theme.path_highlight)
        self.after(PATH_HIGHLIGHT_MS, lambda: self._clear_highlight(path))

    def _clear_highlight(self, path):
        for src, dst in zip(path, path[1:]):
            if (src, dst) in self.edges:
                self.edges[(src, dst)].set_color(self.theme.edge)
        self._restyle_selection()

    def _restyle_selection(self):
        """Repaint every vertex according to its selection state."""
        for name, view in self.nodes.items():
            if self.selection[:1] == [name]:
                view.set_colors(self.theme.source_fill, self.theme.source_outline)
            elif self.selection[1:] == [name]:
                view.set_colors(self.theme.target_fill, self.theme.target_outline)
            else:
                view.set_colors(self.theme.node_fill, self.theme.node_outline)

    def _find_free_spot(self):
        """Pick a random point whose circle stays inside the canvas and away from other vertices."""
        r = NODE_RADIUS
        for _ in range(MAX_PLACEMENT_TRIES):
            x = randint(r + 5, self.winfo_width() - r - 5)
            y = randint(r + 5, self.winfo_height() - r - 5)
            too_close = any(((x - n.x) ** 2 + (y - n.y) ** 2) ** 0.5 < r * 3 for n in self.nodes.values())
            if not too_close and not self.find_overlapping(x - r, y - r, x + r, y + r):
                return x, y
        raise PlacementError("Quantidade de vértices acima do limite\npermitido pelo tamanho da janela.")

    def _drag_node(self, event, name):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
            self.move_node(name, x, y)

    def _show_node_menu(self, event, name):
        self.toggle_selection(name)
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(label="Recomendações")
        menu.add_command(label="Deletar", command=lambda: self._confirm_delete(name))
        menu.tk_popup(event.x_root, event.y_root, 0)

    def _confirm_delete(self, name):
        if messagebox.askyesno("Deletar vértice", "Tem certeza que deseja deletar %s?" % name):
            self.delete_node(name)

    def _change_weight(self, src, dst):
        cost = ask_weight("Mudar peso", "Insira o novo peso:")
        if cost is not None:
            self.graph.add_edge(src, dst, cost)
            self.edges[(src, dst)].set_cost(cost)
            self.on_change()
