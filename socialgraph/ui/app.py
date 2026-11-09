"""Main window: menus and the actions they trigger.

@author: Enzo Suzart Pinto
"""

import os.path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from socialgraph.config import APP_NAME
from socialgraph.model import graph_io
from socialgraph.model.names import name_error, normalize_name
from socialgraph.model.social_graph import BY_DISTANCE, BY_WEIGHTED_DISTANCE, recommend_friends
from socialgraph.theme import DARK
from socialgraph.ui.dialogs import InfoDialog, RecommendationsPopup, UnsavedChangesDialog, ask_weight, clamp_weight
from socialgraph.ui.graph_canvas import GraphCanvas, PlacementError
from socialgraph.ui.widgets import center_window, set_icon

FILE_TYPES = [("Arquivos de texto (*.txt)", "*.txt")]


class SocialGraphApp(tk.Tk):
    """Top-level window.

    `dirty` is True while there are changes not yet exported. Every graph mutation
    must go through mark_dirty() so the unsaved-changes prompt stays reliable.
    """

    def __init__(self):
        super().__init__()
        set_icon(self)
        self.geometry("%dx%d" % (self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2))
        self.dirty = False
        self.file_name = None
        self.canvas = GraphCanvas(self, DARK, on_change=self.mark_dirty, on_recommend=self.show_recommendations)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self._build_menu()
        self._update_title()
        self.protocol("WM_DELETE_WINDOW", lambda: self._run_discarding_changes(self.destroy))

    @property
    def graph(self):
        return self.canvas.graph

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Novo", command=self.new_graph)
        file_menu.add_command(label="Importar", command=self.import_graph)
        file_menu.add_command(label="Exportar", command=self.export_graph)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        create_menu = tk.Menu(menubar, tearoff=False)
        create_menu.add_command(label="Vértice", command=self.add_vertex)
        create_menu.add_command(label="Aresta", command=self.connect_selected)
        menubar.add_cascade(label="Criar...", menu=create_menu)

        menubar.add_command(label="Menor caminho", command=self.show_shortest_path)

        rec_menu = tk.Menu(menubar, tearoff=False)
        rec_menu.add_command(label="Por distância", command=lambda: self.show_recommendations(BY_DISTANCE))
        rec_menu.add_command(label="Por distância ponderada",
                             command=lambda: self.show_recommendations(BY_WEIGHTED_DISTANCE))
        menubar.add_cascade(label="Recomendações", menu=rec_menu)

        menubar.add_command(label="Informações", command=lambda: InfoDialog(self))
        self.configure(menu=menubar)

    def mark_dirty(self):
        self.dirty = True
        self._update_title()

    def mark_clean(self, path=None):
        """Record that the graph matches a file on disk (or is a fresh, empty graph)."""
        self.dirty = False
        self.file_name = os.path.splitext(os.path.basename(path))[0] if path else None
        self._update_title()

    def _update_title(self):
        title = "%s - %s" % (self.file_name, APP_NAME) if self.file_name else APP_NAME
        self.title(("*" if self.dirty else "") + title)

    def _run_discarding_changes(self, action):
        """Run action right away, or after the user decides what to do with unsaved changes."""
        if self.dirty:
            UnsavedChangesDialog(self, action)
        else:
            action()

    # File menu

    def new_graph(self):
        self._run_discarding_changes(self._reset)

    def _reset(self):
        self.canvas.clear()
        self.mark_clean()

    def import_graph(self):
        self._run_discarding_changes(self._choose_and_load)

    def _choose_and_load(self):
        path = filedialog.askopenfilename(filetypes=FILE_TYPES)
        if not path:
            return
        try:
            graph = graph_io.load_graph(path)
            if graph.num_vertices() == 0:
                raise ValueError("O arquivo não gera um grafo.")
        except (OSError, ValueError) as error:
            messagebox.showwarning("Erro!", error)
            return
        self.canvas.load_graph(graph)
        self.mark_clean(path)

    def export_graph(self):
        """Save the graph to a user-chosen file. Return True only if it was written."""
        if self.graph.num_vertices() == 0:
            messagebox.showwarning("Grafo vazio!", "O grafo atual está vazio.")
            return False
        path = filedialog.asksaveasfilename(filetypes=FILE_TYPES, defaultextension=".txt")
        if not path:
            return False
        try:
            graph_io.save_graph(self.graph, path)
        except OSError as error:
            messagebox.showerror("Erro!", "Não foi possível salvar o arquivo:\n%s" % error)
            return False
        self.mark_clean(path)
        return True

    # Graph editing

    def add_vertex(self):
        raw = simpledialog.askstring("Criar vértice", "Insira o nome:")
        if raw is None:
            return
        name = normalize_name(raw)
        error = name_error(name)
        if error:
            messagebox.showwarning("Atenção!", error)
        elif self.graph.has_vertex(name):
            messagebox.showwarning("Atenção!", "O grafo já possui um vértice %s." % name)
        else:
            try:
                self.canvas.add_node(name)
            except PlacementError as error:
                messagebox.showwarning("Atenção!", error)
                return
            self.mark_dirty()

    def connect_selected(self):
        if len(self.canvas.selection) < 2:
            messagebox.showwarning("Atenção!", "Para criar uma aresta, selecione dois vértices.")
            return
        src, dst = self.canvas.selection
        if self.graph.has_edge(src, dst):
            messagebox.showwarning("Atenção!", "Já há uma aresta entre os dois pontos.\nCaso deseje alterar o peso,"
                                               " acesse 'Informações'\npara saber como.")
            return
        cost = ask_weight("Nova aresta", "Insira o peso da aresta:")
        if cost is not None and self.canvas.add_edge(src, dst, cost):
            self.mark_dirty()

    def show_shortest_path(self):
        if len(self.canvas.selection) < 2:
            messagebox.showwarning("Atenção!", "Selecione dois vértices para mostrar o menor caminho.")
            return
        path = self.graph.shortest_path(*self.canvas.selection)
        if path:
            self.canvas.highlight_path(path)
        else:
            messagebox.showwarning("Aviso!", "Não existe um caminho entre os dois vértices selecionados.")

    def show_recommendations(self, option, person=None):
        """Show recommendations for person, or for the single selected vertex if person is None."""
        if person is None:
            if len(self.canvas.selection) != 1:
                messagebox.showwarning("Atenção!", "Selecione um único vértice para obter recomendações.")
                return
            person = self.canvas.selection[0]
        top_k = simpledialog.askinteger("Recomendações", "Insira o número de recomendações:", minvalue=1)
        if top_k is None:
            return
        recommended = recommend_friends(self.graph, person, option, top_k)
        if recommended:
            RecommendationsPopup(self, person, recommended)
        else:
            messagebox.showwarning("Aviso!", "Não há sugestões disponíveis.")

    def add_recommended_edge(self, src, dst, score):
        """Follow a recommendation. The score can exceed the weight range, so it is clamped."""
        if self.graph.has_edge(src, dst):
            messagebox.showwarning("Atenção!", "Aresta já adicionada.")
            return
        if self.canvas.add_edge(src, dst, clamp_weight(score)):
            self.mark_dirty()


def main():
    app = SocialGraphApp()
    center_window(app)
    app.mainloop()


if __name__ == "__main__":
    main()
