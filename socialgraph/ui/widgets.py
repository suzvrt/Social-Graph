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
            label = tk.Label(self, text=body, wraplength=wraplength, justify=tk.LEFT)
            header.configure(command=lambda h=header, lbl=label: self._toggle(h, lbl))
            self._bodies.append(label)

    def _toggle(self, header, label):
        was_open = label.winfo_manager() == "pack"
        for other in self._bodies:
            other.pack_forget()
        if not was_open:
            label.pack(after=header, anchor=tk.NW, pady=(0, 8))
