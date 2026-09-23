from __future__ import annotations

import tkinter as tk
from tkinter import ttk

BACKGROUND = "#f2f3f8"
SURFACE = "#ffffff"
SURFACE_ALT = "#f7f8fc"
BORDER = "#e1e3ec"
TEXT_PRIMARY = "#1f2430"
TEXT_SECONDARY = "#6b7280"
ACCENT = "#4f46e5"
ACCENT_HOVER = "#4338ca"
ACCENT_TEXT = "#ffffff"
DANGER = "#dc2626"
DANGER_HOVER = "#fdecec"
CANVAS_BACKGROUND = "#dde1ea"
SELECTION = "#e8e6fb"

FONT_FAMILY = "Segoe UI"
FONT_BASE = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_HEADING = (FONT_FAMILY, 17, "bold")
FONT_SMALL = (FONT_FAMILY, 9)


def apply_theme(root: tk.Tk) -> None:
    """Configures a single, consistent visual style for every ttk widget in the app."""
    root.configure(background=BACKGROUND)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", font=FONT_BASE, background=BACKGROUND, foreground=TEXT_PRIMARY)

    style.configure("TFrame", background=BACKGROUND)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure("Toolbar.TFrame", background=SURFACE)
    style.configure("Card.TFrame", background=SURFACE, relief="flat")

    style.configure("TLabel", background=BACKGROUND, foreground=TEXT_PRIMARY)
    style.configure("Surface.TLabel", background=SURFACE, foreground=TEXT_PRIMARY)
    style.configure("Heading.TLabel", background=BACKGROUND, foreground=TEXT_PRIMARY, font=FONT_HEADING)
    style.configure("Subtitle.TLabel", background=BACKGROUND, foreground=TEXT_SECONDARY, font=FONT_SMALL)
    style.configure("Toolbar.TLabel", background=SURFACE, foreground=TEXT_PRIMARY, font=FONT_BOLD)
    style.configure("Muted.TLabel", background=SURFACE, foreground=TEXT_SECONDARY, font=FONT_SMALL)
    style.configure("MutedOnBg.TLabel", background=BACKGROUND, foreground=TEXT_SECONDARY, font=FONT_SMALL)

    style.configure(
        "TButton",
        font=FONT_BASE,
        padding=(12, 7),
        background=SURFACE,
        foreground=TEXT_PRIMARY,
        borderwidth=1,
        bordercolor=BORDER,
        relief="flat",
        focuscolor=BACKGROUND,
    )
    style.map(
        "TButton",
        background=[("active", SURFACE_ALT), ("disabled", SURFACE)],
        foreground=[("disabled", TEXT_SECONDARY)],
    )

    style.configure(
        "Accent.TButton",
        font=FONT_BOLD,
        padding=(16, 9),
        background=ACCENT,
        foreground=ACCENT_TEXT,
        borderwidth=0,
        focuscolor=ACCENT,
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_HOVER), ("disabled", "#c7c9d9")],
    )

    style.configure(
        "Danger.TButton",
        font=FONT_BASE,
        padding=(12, 7),
        background=SURFACE,
        foreground=DANGER,
        borderwidth=1,
        bordercolor=BORDER,
    )
    style.map(
        "Danger.TButton",
        background=[("active", DANGER_HOVER)],
    )

    style.configure(
        "Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=TEXT_PRIMARY,
        rowheight=34,
        borderwidth=0,
        font=FONT_BASE,
    )
    style.configure(
        "Treeview.Heading",
        font=FONT_BOLD,
        background=SURFACE_ALT,
        foreground=TEXT_SECONDARY,
        relief="flat",
        padding=(8, 8),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", SURFACE_ALT)],
    )
    style.map(
        "Treeview",
        background=[("selected", SELECTION)],
        foreground=[("selected", ACCENT)],
    )
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    style.configure("TNotebook", background=BACKGROUND, borderwidth=0, tabmargins=(0, 6, 0, 0))
    style.configure(
        "TNotebook.Tab",
        font=FONT_BOLD,
        padding=(16, 9),
        background=BACKGROUND,
        foreground=TEXT_SECONDARY,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", SURFACE)],
        foreground=[("selected", ACCENT)],
    )

    style.configure(
        "TEntry",
        padding=7,
        fieldbackground=SURFACE,
        borderwidth=1,
        bordercolor=BORDER,
        foreground=TEXT_PRIMARY,
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    scrollbar_thumb = "#c3c6d6"
    scrollbar_thumb_active = "#9ca0b8"
    style.configure(
        "Vertical.TScrollbar",
        background=scrollbar_thumb,
        troughcolor=SURFACE_ALT,
        bordercolor=SURFACE_ALT,
        lightcolor=scrollbar_thumb,
        darkcolor=scrollbar_thumb,
        borderwidth=0,
        arrowsize=13,
        relief="flat",
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=scrollbar_thumb,
        troughcolor=SURFACE_ALT,
        bordercolor=SURFACE_ALT,
        lightcolor=scrollbar_thumb,
        darkcolor=scrollbar_thumb,
        borderwidth=0,
        arrowsize=13,
        relief="flat",
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", scrollbar_thumb_active), ("pressed", scrollbar_thumb_active)],
        lightcolor=[("active", scrollbar_thumb_active), ("pressed", scrollbar_thumb_active)],
        darkcolor=[("active", scrollbar_thumb_active), ("pressed", scrollbar_thumb_active)],
    )
    style.map(
        "Horizontal.TScrollbar",
        background=[("active", scrollbar_thumb_active), ("pressed", scrollbar_thumb_active)],
        lightcolor=[("active", scrollbar_thumb_active), ("pressed", scrollbar_thumb_active)],
        darkcolor=[("active", scrollbar_thumb_active), ("pressed", scrollbar_thumb_active)],
    )

    style.configure("TSeparator", background=BORDER)

    style.configure(
        "Progress.Horizontal.TProgressbar",
        background=ACCENT,
        troughcolor=SURFACE_ALT,
        borderwidth=0,
        thickness=6,
    )


def style_listbox(listbox: tk.Listbox) -> None:
    """Applies the shared visual style to a plain tk.Listbox widget."""
    listbox.configure(
        background=SURFACE,
        foreground=TEXT_PRIMARY,
        selectbackground=SELECTION,
        selectforeground=ACCENT,
        activestyle="none",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        font=FONT_BASE,
    )
