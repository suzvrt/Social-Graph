"""Main window: menus and the actions they trigger.

@author: Enzo Suzart Pinto
"""

import os.path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from socialgraph.config import APP_NAME
from socialgraph.model import graph_io
from socialgraph.model.social_graph import BY_DISTANCE, BY_WEIGHTED_DISTANCE, recommend_friends
from socialgraph.theme import DARK
from socialgraph.ui.dialogs import InfoDialog, RecommendationsPopup, UnsavedChangesDialog, ask_weight
from socialgraph.ui.graph_canvas import GraphCanvas, PlacementError
from socialgraph.ui.widgets import center_window, set_icon

FILE_TYPES = [("Arquivos de texto (*.txt)", "*.txt")]


class SocialGraphApp(tk.Tk):
    """Top-level window. `dirty` is True while there are changes not yet exported."""

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        set_icon(self)
        self.geometry("%dx%d" % (self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2))
        self.dirty = False
        self.canvas = GraphCanvas(self, DARK, on_change=self._on_graph_changed)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self._build_menu()

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

    def _on_graph_changed(self):
        self.dirty = True

    def _set_file_title(self, path):
        self.title("%s - %s" % (os.path.splitext(os.path.basename(path))[0], APP_NAME))

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
        self.title(APP_NAME)

    def import_graph(self):
        self._run_discarding_changes(self._choose_and_load)

    def _choose_and_load(self):
        path = filedialog.askopenfilename(filetypes=FILE_TYPES)
        if not path:
            return
        self._reset()
        try:
            graph = graph_io.load_graph(path)
            if graph.num_vertices() == 0:
                raise ValueError("O arquivo não gera um grafo.")
            self.canvas.load_graph(graph)
            self._set_file_title(path)
        except Exception as error:
            self._reset()
            messagebox.showwarning("Erro!", error)

    def export_graph(self):
        if self.graph.num_vertices() == 0:
            messagebox.showwarning("Grafo vazio!", "O grafo atual está vazio.")
            return
        path = filedialog.asksaveasfilename(filetypes=FILE_TYPES)
        if not path:
            return
        if not path.endswith(".txt"):
            path += ".txt" if not os.path.isfile(path + ".txt") else " (1).txt"
        graph_io.save_graph(self.graph, path)
        self._set_file_title(path)
        self.dirty = False

    # Graph editing

    def add_vertex(self):
        name = simpledialog.askstring("Criar vértice", "Insira o nome:")
        if not name:
            return
        if self.graph.has_vertex(name):
            messagebox.showwarning("Atenção!", "O grafo já possui um vértice %s." % name)
        elif not name.isalpha():
            messagebox.showwarning("Atenção!", "Números e símbolos não permitidos.")
        else:
            try:
                self.canvas.add_node(name.capitalize())
            except PlacementError as error:
                messagebox.showwarning("Atenção!", error)
                return
            self.dirty = True

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
        if cost is not None:
            self.canvas.add_edge(src, dst, cost)
            self.dirty = True

    def show_shortest_path(self):
        if len(self.canvas.selection) < 2:
            messagebox.showwarning("Atenção!", "Selecione dois vértices para mostrar o menor caminho.")
            return
        path = self.graph.shortest_path(*self.canvas.selection)
        if path:
            self.canvas.highlight_path(path)
        else:
            messagebox.showwarning("Aviso!", "Não existe um caminho entre os dois vértices selecionados.")

    def show_recommendations(self, option):
        selection = self.canvas.selection
        if len(selection) > 1:
            messagebox.showwarning("Atenção!", "Selecione apenas um vértice")
        if not selection:
            messagebox.showwarning("Atenção!", "Selecione um vértice para obter recomendações.")
            return
        top_k = simpledialog.askinteger("Recomendações", "Insira o número de recomendações:")
        if top_k is None:
            return
        recommended = recommend_friends(self.graph, selection[0], option, top_k)
        if recommended:
            RecommendationsPopup(self, selection[0], recommended)
        else:
            messagebox.showwarning("Aviso!", "Não há sugestões disponíveis.")

    def add_recommended_edge(self, src, dst, cost):
        if self.graph.has_edge(src, dst):
            messagebox.showwarning("Atenção!", "Aresta já adicionada.")
            return
        self.canvas.add_edge(src, dst, cost)
        self.dirty = True


def main():
    app = SocialGraphApp()
    center_window(app)
    app.mainloop()


if __name__ == "__main__":
    main()
