"""Small reusable Tk helpers shared by the main window and dialogs."""

import tkinter as tk

from socialgraph.config import FONT_FAMILY, ICON_PATH


def center_window(window, y_offset=-50):
    """Place window in the middle of the screen, keeping its current size."""
    window.update_idletasks()
    width, height = window.winfo_width(), window.winfo_height()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2 + y_offset
    window.geometry("%dx%d+%d+%d" % (width, height, x, y))


def set_icon(window):
    # .ico files are only supported by Tk on Windows.
    try:
        window.iconbitmap(str(ICON_PATH))
    except tk.TclError:
        pass


class Accordion(tk.Frame):
    """Vertical list of collapsible (title, body) topics where at most one is expanded."""

    def __init__(self, master, topics, wraplength, **kwargs):
        super().__init__(master, **kwargs)
        self._bodies = []
        for title, body in topics:
            header = tk.Button(self, text="○ %s:" % title, font=(FONT_FAMILY, 9, "bold"), borderwidth=0)
            header.pack(anchor=tk.NW)
            label = tk.Label(self, text="", wraplength=wraplength, justify=tk.LEFT)
            label.pack(anchor=tk.NW)
            header.configure(command=lambda lbl=label, text=body: self._toggle(lbl, text))
            self._bodies.append(label)

    def _toggle(self, label, body):
        was_open = bool(label.cget("text"))
        for other in self._bodies:
            other.configure(text="")
        if not was_open:
            label.configure(text=body + "\n")
