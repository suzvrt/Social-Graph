"""Secondary windows: unsaved-changes prompt, recommendations table and help."""

import tkinter as tk
from tkinter import simpledialog, ttk

from socialgraph.config import APP_NAME, FONT_FAMILY, MAX_WEIGHT, MIN_WEIGHT
from socialgraph.ui import help_content
from socialgraph.ui.widgets import Accordion, center_window, set_icon


def clamp_weight(cost):
    return max(MIN_WEIGHT, min(MAX_WEIGHT, int(cost)))


def ask_weight(title, prompt):
    """Ask for an edge weight, clamped to the allowed range. Return None if cancelled."""
    cost = simpledialog.askinteger(title, prompt)
    return None if cost is None else clamp_weight(cost)


class UnsavedChangesDialog(tk.Toplevel):
    """Modal prompt offering to export before an action that discards the current graph."""

    def __init__(self, app, on_continue):
        super().__init__(app)
        self.app = app
        self.on_continue = on_continue
        self.title("Atenção!")
        self.resizable(False, False)
        self.geometry("230x100+%d+%d" % (self.winfo_screenwidth() // 2 - 115, self.winfo_screenheight() // 2 - 50))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        tk.Label(self, text="Mudanças não salvas, deseja:").grid(row=1, column=1, columnspan=3, sticky=tk.NS)
        ttk.Button(self, text="Exportar", command=self.save_and_continue).grid(row=2, column=1, sticky=tk.SW)
        ttk.Button(self, text="Continuar", command=self.discard_and_continue).grid(row=2, column=2)
        ttk.Button(self, text="Cancelar", command=self.destroy).grid(row=2, column=3, sticky=tk.E)
        self.grab_set()
        self.focus_set()

    def save_and_continue(self):
        # Stay open if the user cancels the save dialog, so the changes are not lost silently.
        if self.app.export_graph():
            self.discard_and_continue()

    def discard_and_continue(self):
        self.destroy()
        self.on_continue()


class RecommendationsPopup(tk.Toplevel):
    """Table of recommended friends, each with a button to create the edge."""

    def __init__(self, app, person, recommended):
        super().__init__(app)
        self.title("Recomendações - %s" % APP_NAME)
        self.resizable(False, False)
        for col in range(3):
            self.columnconfigure(col, weight=1)
        bold = (FONT_FAMILY, 9, "bold")
        for col, header in enumerate(("Nome", "Peso", "Opção")):
            tk.Label(self, text=header, font=bold).grid(row=0, column=col, sticky=tk.NSEW)
        for row, edge in enumerate(recommended, start=1):
            tk.Label(self, text=edge.vertex).grid(row=row, column=0, sticky=tk.NSEW)
            tk.Label(self, text=edge.cost).grid(row=row, column=1, sticky=tk.NSEW)
            ttk.Button(self, text="Adicionar",
                       command=lambda d=edge.vertex, c=edge.cost: app.add_recommended_edge(person, d, c)
                       ).grid(row=row, column=2, sticky=tk.NSEW)
        center_window(self)


class InfoDialog(tk.Toplevel):
    """Help window with usage instructions and information about the project."""

    def __init__(self, app):
        super().__init__(app)
        self.geometry("%dx%d" % (self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2))
        self.resizable(False, False)
        set_icon(self)
        self.title("Informações - %s" % APP_NAME)
        center_window(self)

        wrap = self.winfo_screenwidth() // 2 - 30
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill=tk.BOTH)
        ttk.Button(self, text="Fechar", command=self.destroy).pack(anchor=tk.S)

        manual = self._add_tab(notebook, "Como usar")
        Accordion(manual, help_content.HOW_TO, wrap).pack(anchor=tk.NW, fill=tk.X)

        more = self._add_tab(notebook, "Mais")
        Accordion(more, help_content.MORE, wrap).pack(anchor=tk.NW, fill=tk.X)
        tk.Label(more, text="__________________________________").pack(anchor=tk.S)
        tk.Label(more, text="Sobre o projeto", font=(FONT_FAMILY, 10, "bold")).pack(anchor=tk.S)
        tk.Label(more, text=help_content.ABOUT, wraplength=wrap, justify=tk.LEFT).pack(anchor=tk.S)

        self.grab_set()
        self.focus_set()

    @staticmethod
    def _add_tab(notebook, title):
        frame = tk.Frame(notebook, bd=3)
        notebook.add(frame, text=title)
        tk.Label(frame, text="(Clique no item desejado para expandí-lo.)", font=(FONT_FAMILY, 9, "italic"),
                 fg="dark gray").pack(anchor=tk.NW)
        return frame
