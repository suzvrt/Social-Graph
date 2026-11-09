"""Interactive canvas that keeps the drawing in sync with a DiGraph."""

import tkinter as tk
from random import randint
from tkinter import messagebox

from socialgraph.config import EDGE_CLEARANCE, MAX_PLACEMENT_TRIES, NODE_RADIUS, PATH_HIGHLIGHT_MS
from socialgraph.model.digraph import DiGraph
from socialgraph.model.social_graph import BY_DISTANCE, BY_WEIGHTED_DISTANCE
from socialgraph.ui.dialogs import ask_weight
from socialgraph.ui.edge_view import EdgeView
from socialgraph.ui.geometry import force_layout, route_distance, route_edge
from socialgraph.ui.node_view import NodeView


class PlacementError(Exception):
    """Raised when there is no free room left on the canvas for a new vertex."""


class GraphCanvas(tk.Canvas):
    """Owns the graph model and its views, and handles mouse interaction with them.

    Selection holds up to two vertex names: index 0 is the source (green) and
    index 1 the destination (purple) used by edge creation and shortest path.
    """

    def __init__(self, master, theme, on_change, on_recommend):
        super().__init__(master, bg=theme.canvas_bg, highlightthickness=0)
        self.theme = theme
        self.on_change = on_change
        self.on_recommend = on_recommend
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
        """Replace the current drawing with graph, positioned by a force-directed layout."""
        self.clear()
        margin = NODE_RADIUS + 5
        positions = force_layout(graph.vertices(), [(src, dst) for src, _, dst in graph.edges()],
                                 self.winfo_width(), self.winfo_height(), margin, min_distance=3 * NODE_RADIUS)
        for vertex, position in positions.items():
            self._create_node(vertex, *position)
        for src, cost, dst in graph.edges():
            self._create_edge(src, dst, cost)
        self._reroute_edges()

    def add_node(self, name):
        """Add a vertex at a random free spot. Raise PlacementError if the canvas is full."""
        if self.graph.has_vertex(name):
            return
        self._create_node(name, *self._find_free_spot())
        self._reroute_edges()

    def add_edge(self, src, dst, cost):
        """Create src -> dst, or update its weight if it exists. Return False if the model rejects it."""
        if (src, dst) in self.edges:
            if not self.graph.add_edge(src, dst, cost):
                return False
            self.edges[(src, dst)].set_cost(cost)
            return True
        if not self._create_edge(src, dst, cost):
            return False
        self._reroute_edges()
        return True

    def delete_edge(self, src, dst):
        if self.graph.remove_edge(src, dst):
            self.edges.pop((src, dst)).delete()
            self._reroute_edges()

    def delete_node(self, name):
        self.graph.remove_vertex(name)
        for key in [key for key in self.edges if name in key]:
            self.edges.pop(key).delete()
        self.nodes.pop(name).delete()
        if name in self.selection:
            self.selection.remove(name)
            self._restyle_selection()
        self._reroute_edges()

    def move_node(self, name, x, y):
        view = self.nodes[name]
        old = (view.x, view.y)
        view.move_to(x, y)
        # Only edges touching the vertex, passing near its old or new spot, or already
        # bent around something can change; this keeps dragging smooth on larger graphs.
        reach = NODE_RADIUS + EDGE_CLEARANCE
        for (src, dst), edge in self.edges.items():
            if (name in (src, dst) or edge.route.curved
                    or route_distance(edge.route, old) < reach or route_distance(edge.route, (x, y)) < reach):
                edge.redraw(self._route(src, dst))

    def _create_node(self, name, x, y):
        self.graph.add_vertex(name)
        view = NodeView(self, name, x, y, self.theme)
        view.bind("<Button-3>", lambda e: self._show_node_menu(e, name))
        view.bind("<B1-Motion>", lambda e: self._drag_node(e, name))
        view.bind("<Control-1>", lambda e: self.toggle_selection(name))
        self.nodes[name] = view

    def _create_edge(self, src, dst, cost):
        if not self.graph.add_edge(src, dst, cost):
            return False
        view = EdgeView(self, cost, self.theme, self._route(src, dst))
        view.bind("<Double-Button-1>", lambda e: self._change_weight(src, dst))
        view.bind("<Button-3>", lambda e: self._show_edge_menu(e, src, dst))
        self.edges[(src, dst)] = view
        return True

    def _route(self, src, dst):
        a, b = self.nodes[src], self.nodes[dst]
        obstacles = [(n.x, n.y) for name, n in self.nodes.items() if name not in (src, dst)]
        return route_edge((a.x, a.y), (b.x, b.y), NODE_RADIUS, obstacles, self.graph.has_edge(dst, src))

    def _reroute_edges(self):
        # Any change can open or block another edge's path (or create/remove its reverse
        # edge), so every edge is rerouted. Fine for the graph sizes this app targets.
        for (src, dst), view in self.edges.items():
            view.redraw(self._route(src, dst))

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

    def apply_theme(self, theme):
        """Recolor every item in place; nothing is redrawn or moved."""
        self.theme = theme
        self.configure(bg=theme.canvas_bg)
        for view in self.nodes.values():
            view.set_text_color(theme.node_text)
        for view in self.edges.values():
            view.apply_theme(theme)
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
        menu = tk.Menu(self, tearoff=False)
        rec_menu = tk.Menu(menu, tearoff=False)
        rec_menu.add_command(label="Por distância", command=lambda: self.on_recommend(BY_DISTANCE, name))
        rec_menu.add_command(label="Por distância ponderada",
                             command=lambda: self.on_recommend(BY_WEIGHTED_DISTANCE, name))
        menu.add_cascade(label="Recomendações", menu=rec_menu)
        menu.add_command(label="Deletar", command=lambda: self._confirm_delete(name))
        menu.tk_popup(event.x_root, event.y_root, 0)

    def _show_edge_menu(self, event, src, dst):
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(label="Alterar peso", command=lambda: self._change_weight(src, dst))
        menu.add_command(label="Excluir aresta", command=lambda: self._confirm_delete_edge(src, dst))
        menu.tk_popup(event.x_root, event.y_root, 0)

    def _confirm_delete_edge(self, src, dst):
        if messagebox.askyesno("Excluir aresta", "Tem certeza que deseja excluir a aresta %s → %s?" % (src, dst)):
            self.delete_edge(src, dst)
            self.on_change()

    def _confirm_delete(self, name):
        message = "Tem certeza que deseja deletar %s?" % name
        affected = len(self.graph.adjacent_to(name)) + len(self.graph.incoming_edges(name))
        if affected == 1:
            message += "\n1 aresta também será removida."
        elif affected > 1:
            message += "\n%d arestas também serão removidas." % affected
        if messagebox.askyesno("Deletar vértice", message):
            self.delete_node(name)
            self.on_change()

    def _change_weight(self, src, dst):
        cost = ask_weight("Mudar peso", "Insira o novo peso:")
        if cost is not None and self.add_edge(src, dst, cost):
            self.on_change()
