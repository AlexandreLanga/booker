from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from application.dto import AnnotationView
from domain.value_objects import SearchResult
from presentation.theme import CANVAS_BACKGROUND, style_listbox


class ReaderScreen(ttk.Frame):
    """Displays a single PDF page with navigation, search and annotations."""

    def __init__(
        self,
        master,
        on_back: Callable[[], None],
        on_page_changed: Callable[[int], None],
        on_search: Callable[[str], list[SearchResult]],
        on_add_annotation: Callable[[int, str], None],
        on_delete_annotation: Callable[[int], None],
    ):
        super().__init__(master, style="TFrame")
        self._on_back = on_back
        self._on_page_changed = on_page_changed
        self._on_search = on_search
        self._on_add_annotation = on_add_annotation
        self._on_delete_annotation = on_delete_annotation

        self._total_pages = 0
        self._current_page = 0
        self._page_image: tk.PhotoImage | None = None
        self._render_page_callback: Callable[[int], bytes] | None = None
        self._search_results: list[SearchResult] = []
        self._annotation_ids: list[int] = []

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self) -> None:
        toolbar = ttk.Frame(self, style="Toolbar.TFrame", borderwidth=1, relief="solid")
        toolbar.pack(fill="x")

        toolbar_inner = ttk.Frame(toolbar, style="Toolbar.TFrame")
        toolbar_inner.pack(fill="x", padx=16, pady=10)

        ttk.Button(toolbar_inner, text="←  Biblioteca", command=self._on_back).pack(side="left")

        nav_box = ttk.Frame(toolbar_inner, style="Toolbar.TFrame")
        nav_box.pack(side="left", padx=(24, 0))
        ttk.Button(nav_box, text="◀", width=3, command=self._go_previous).pack(side="left")
        self._page_label = ttk.Label(nav_box, text="Página 0 / 0", style="Toolbar.TLabel", width=16, anchor="center")
        self._page_label.pack(side="left", padx=8)
        ttk.Button(nav_box, text="▶", width=3, command=self._go_next).pack(side="left")

        self._progress = ttk.Progressbar(
            toolbar_inner, style="Progress.Horizontal.TProgressbar", maximum=1, value=0, length=160
        )
        self._progress.pack(side="left", padx=(20, 0))

        search_box = ttk.Frame(toolbar_inner, style="Toolbar.TFrame")
        search_box.pack(side="right")
        self._search_entry = ttk.Entry(search_box, width=32)
        self._search_entry.pack(side="left")
        self._search_entry.bind("<Return>", lambda _event: self._handle_search())
        ttk.Button(search_box, text="🔍  Pesquisar", command=self._handle_search).pack(side="left", padx=(6, 0))

        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        canvas_frame = ttk.Frame(body, style="Card.TFrame", borderwidth=1, relief="solid")
        canvas_frame.pack(side="left", fill="both", expand=True)

        y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal")
        self._canvas = tk.Canvas(
            canvas_frame,
            background=CANVAS_BACKGROUND,
            highlightthickness=0,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )
        y_scroll.config(command=self._canvas.yview)
        x_scroll.config(command=self._canvas.xview)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self._canvas.pack(side="left", fill="both", expand=True)

        side_panel = ttk.Frame(body, style="TFrame", width=320)
        side_panel.pack(side="right", fill="y", padx=(16, 0))
        side_panel.pack_propagate(False)

        notebook = ttk.Notebook(side_panel)
        notebook.pack(fill="both", expand=True)

        annotations_tab = ttk.Frame(notebook, style="Surface.TFrame")
        search_tab = ttk.Frame(notebook, style="Surface.TFrame")
        notebook.add(annotations_tab, text="📝 Anotações")
        notebook.add(search_tab, text="🔎 Resultados")

        self._annotations_list = tk.Listbox(annotations_tab)
        style_listbox(self._annotations_list)
        self._annotations_list.pack(fill="both", expand=True, padx=10, pady=(10, 8))

        annotation_form = ttk.Frame(annotations_tab, style="Surface.TFrame")
        annotation_form.pack(fill="x", padx=10, pady=(0, 8))
        self._annotation_entry = ttk.Entry(annotation_form)
        self._annotation_entry.pack(side="left", fill="x", expand=True)
        self._annotation_entry.bind("<Return>", lambda _event: self._handle_add_annotation())
        ttk.Button(annotation_form, text="＋", width=3, command=self._handle_add_annotation).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(
            annotations_tab,
            text="🗑  Remover selecionada",
            style="Danger.TButton",
            command=self._handle_delete_annotation,
        ).pack(fill="x", padx=10, pady=(0, 10))

        self._search_results_list = tk.Listbox(search_tab)
        style_listbox(self._search_results_list)
        self._search_results_list.pack(fill="both", expand=True, padx=10, pady=10)

    def _bind_events(self) -> None:
        self._search_results_list.bind("<Double-1>", lambda _event: self._handle_open_search_result())

    def load_book(
        self,
        title: str,
        total_pages: int,
        current_page: int,
        render_page_callback: Callable[[int], bytes],
    ) -> None:
        self._total_pages = total_pages
        self._render_page_callback = render_page_callback
        self._progress.configure(maximum=max(total_pages, 1))
        self._search_results = []
        self._search_results_list.delete(0, "end")
        self.show_page(current_page)

    def show_page(self, page_number: int) -> None:
        if self._render_page_callback is None:
            return
        self._current_page = max(0, min(page_number, self._total_pages - 1))
        raw_ppm = self._render_page_callback(self._current_page)
        self._page_image = tk.PhotoImage(data=raw_ppm)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, anchor="nw", image=self._page_image)
        self._canvas.config(scrollregion=self._canvas.bbox("all"))
        self._page_label.config(text=f"Página {self._current_page + 1} / {self._total_pages}")
        self._progress.configure(value=self._current_page + 1)

    def show_annotations(self, annotations: list[AnnotationView]) -> None:
        self._annotation_ids = [annotation.id for annotation in annotations]
        self._annotations_list.delete(0, "end")
        if not annotations:
            self._annotations_list.insert("end", "Nenhuma anotação ainda.")
            self._annotations_list.itemconfig(0, foreground="#9aa0ac")
            return
        for annotation in annotations:
            self._annotations_list.insert("end", f"  📌 p.{annotation.page_number + 1} — {annotation.content}")

    def show_search_results(self, results: list[SearchResult]) -> None:
        self._search_results = results
        self._search_results_list.delete(0, "end")
        if not results:
            self._search_results_list.insert("end", "Nenhum resultado encontrado.")
            self._search_results_list.itemconfig(0, foreground="#9aa0ac")
            return
        for result in results:
            self._search_results_list.insert("end", f"  p.{result.page_number + 1} — {result.snippet}")

    def show_error(self, message: str) -> None:
        messagebox.showerror("Erro", message)

    def _go_previous(self) -> None:
        if self._current_page > 0:
            self._on_page_changed(self._current_page - 1)

    def _go_next(self) -> None:
        if self._current_page < self._total_pages - 1:
            self._on_page_changed(self._current_page + 1)

    def _handle_search(self) -> None:
        query = self._search_entry.get().strip()
        if query:
            self.show_search_results(self._on_search(query))

    def _handle_open_search_result(self) -> None:
        selection = self._search_results_list.curselection()
        if selection and self._search_results:
            result = self._search_results[selection[0]]
            self._on_page_changed(result.page_number)

    def _handle_add_annotation(self) -> None:
        content = self._annotation_entry.get().strip()
        if content:
            self._on_add_annotation(self._current_page, content)
            self._annotation_entry.delete(0, "end")

    def _handle_delete_annotation(self) -> None:
        selection = self._annotations_list.curselection()
        if selection and self._annotation_ids:
            annotation_id = self._annotation_ids[selection[0]]
            self._on_delete_annotation(annotation_id)
