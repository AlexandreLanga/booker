from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from application.dto import AnnotationView
from domain.value_objects import SearchResult
from presentation.theme import CANVAS_BACKGROUND, style_listbox


class ReaderScreen(ttk.Frame):
    """Displays a single PDF page with navigation, search and annotations."""

    _DEFAULT_ZOOM = 1.5
    _MIN_ZOOM_FACTOR = 0.4
    _MAX_ZOOM_FACTOR = 3.0
    _ZOOM_STEP = 1.15
    _INITIAL_ZOOM_FACTOR = 0.75

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
        self._render_page_callback: Callable[[int, float], bytes] | None = None
        self._search_results: list[SearchResult] = []
        self._annotation_ids: list[int] = []
        self._zoom_factor = self._INITIAL_ZOOM_FACTOR
        self._image_item: int | None = None
        self._image_offset = (0, 0)
        self._image_size = (0, 0)
        self._scroll_region_size = (0, 0)

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

        zoom_box = ttk.Frame(toolbar_inner, style="Toolbar.TFrame")
        zoom_box.pack(side="left", padx=(20, 0))
        self._zoom_out_button = ttk.Button(zoom_box, text="－", width=3, command=self._handle_zoom_out)
        self._zoom_out_button.pack(side="left")
        self._zoom_label = ttk.Label(
            zoom_box, text="100%", style="Toolbar.TLabel", width=6, anchor="center", cursor="hand2"
        )
        self._zoom_label.pack(side="left", padx=4)
        self._zoom_label.bind("<Double-Button-1>", lambda _event: self._handle_zoom_reset())
        self._zoom_in_button = ttk.Button(zoom_box, text="＋", width=3, command=self._handle_zoom_in)
        self._zoom_in_button.pack(side="left")

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
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self._y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical")
        self._x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal")
        self._canvas = tk.Canvas(
            canvas_frame,
            background=CANVAS_BACKGROUND,
            highlightthickness=0,
            yscrollcommand=self._y_scroll.set,
            xscrollcommand=self._x_scroll.set,
        )
        self._y_scroll.config(command=self._canvas.yview)
        self._x_scroll.config(command=self._canvas.xview)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._y_scroll.grid(row=0, column=1, sticky="ns")
        self._x_scroll.grid(row=1, column=0, sticky="ew")
        self._y_scroll_visible = True
        self._x_scroll_visible = True

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

        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self._canvas.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        self._canvas.bind("<Button-4>", self._on_mousewheel)
        self._canvas.bind("<Button-5>", self._on_mousewheel)
        self._canvas.bind("<Shift-Button-4>", self._on_shift_mousewheel)
        self._canvas.bind("<Shift-Button-5>", self._on_shift_mousewheel)
        self._canvas.bind("<Control-Button-4>", self._on_ctrl_mousewheel)
        self._canvas.bind("<Control-Button-5>", self._on_ctrl_mousewheel)
        self._canvas.bind("<Configure>", lambda _event: self._reposition_image())

    def load_book(
        self,
        title: str,
        total_pages: int,
        current_page: int,
        render_page_callback: Callable[[int, float], bytes],
    ) -> None:
        self._total_pages = total_pages
        self._render_page_callback = render_page_callback
        self._progress.configure(maximum=max(total_pages, 1))
        self._search_results = []
        self._search_results_list.delete(0, "end")
        self._zoom_factor = self._INITIAL_ZOOM_FACTOR
        self._update_zoom_controls()
        self.show_page(current_page)

    def show_page(self, page_number: int) -> None:
        if self._render_page_callback is None:
            return
        self._current_page = max(0, min(page_number, self._total_pages - 1))
        self._render_current_page()
        self._page_label.config(text=f"Página {self._current_page + 1} / {self._total_pages}")
        self._progress.configure(value=self._current_page + 1)

    def _render_current_page(self) -> None:
        if self._render_page_callback is None:
            return
        zoom = self._DEFAULT_ZOOM * self._zoom_factor
        raw_ppm = self._render_page_callback(self._current_page, zoom)
        self._page_image = tk.PhotoImage(data=raw_ppm)
        self._canvas.delete("all")
        self._image_item = self._canvas.create_image(0, 0, anchor="nw", image=self._page_image)
        self._reposition_image()

    def _reposition_image(self) -> None:
        if self._page_image is None or self._image_item is None:
            return
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        img_width = self._page_image.width()
        img_height = self._page_image.height()
        offset_x = max(0, (canvas_width - img_width) // 2)
        offset_y = max(0, (canvas_height - img_height) // 2)
        region_width = max(canvas_width, img_width)
        region_height = max(canvas_height, img_height)
        self._canvas.coords(self._image_item, offset_x, offset_y)
        self._canvas.config(scrollregion=(0, 0, region_width, region_height))
        self._image_offset = (offset_x, offset_y)
        self._image_size = (img_width, img_height)
        self._scroll_region_size = (region_width, region_height)
        self._set_scrollbar_visible(self._x_scroll, "_x_scroll_visible", img_width > canvas_width + 1)
        self._set_scrollbar_visible(self._y_scroll, "_y_scroll_visible", img_height > canvas_height + 1)

    def _set_scrollbar_visible(self, scrollbar: ttk.Scrollbar, flag_name: str, visible: bool) -> None:
        if getattr(self, flag_name) == visible:
            return
        if visible:
            scrollbar.grid()
        else:
            scrollbar.grid_remove()
        setattr(self, flag_name, visible)

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

    def _on_mousewheel(self, event) -> None:
        if getattr(event, "num", None) == 4:
            self._canvas.yview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self._canvas.yview_scroll(3, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)) * 3, "units")

    def _on_shift_mousewheel(self, event) -> None:
        if getattr(event, "num", None) == 4:
            self._canvas.xview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self._canvas.xview_scroll(3, "units")
        else:
            self._canvas.xview_scroll(int(-1 * (event.delta / 120)) * 3, "units")

    def _on_ctrl_mousewheel(self, event) -> None:
        if getattr(event, "num", None) == 4:
            factor = self._ZOOM_STEP
        elif getattr(event, "num", None) == 5:
            factor = 1 / self._ZOOM_STEP
        else:
            factor = self._ZOOM_STEP if event.delta > 0 else 1 / self._ZOOM_STEP
        self._zoom_at_point(factor, event.x, event.y)

    def _handle_zoom_in(self) -> None:
        self._zoom_at_center(self._ZOOM_STEP)

    def _handle_zoom_out(self) -> None:
        self._zoom_at_center(1 / self._ZOOM_STEP)

    def _handle_zoom_reset(self) -> None:
        if self._zoom_factor == 1.0:
            return
        self._zoom_at_center(1 / self._zoom_factor)

    def _zoom_at_center(self, factor: float) -> None:
        center_x = self._canvas.winfo_width() / 2
        center_y = self._canvas.winfo_height() / 2
        self._zoom_at_point(factor, center_x, center_y)

    def _zoom_at_point(self, factor: float, widget_x: float, widget_y: float) -> None:
        if self._render_page_callback is None or self._page_image is None:
            return
        new_factor = max(self._MIN_ZOOM_FACTOR, min(self._zoom_factor * factor, self._MAX_ZOOM_FACTOR))
        if abs(new_factor - self._zoom_factor) < 1e-6:
            return

        old_width, old_height = self._image_size
        old_offset_x, old_offset_y = self._image_offset
        anchor_x = self._canvas.canvasx(widget_x) - old_offset_x
        anchor_y = self._canvas.canvasy(widget_y) - old_offset_y
        relative_x = min(1.0, max(0.0, anchor_x / old_width)) if old_width else 0.5
        relative_y = min(1.0, max(0.0, anchor_y / old_height)) if old_height else 0.5

        self._zoom_factor = new_factor
        self._render_current_page()
        self._update_zoom_controls()

        new_width, new_height = self._image_size
        new_offset_x, new_offset_y = self._image_offset
        region_width, region_height = self._scroll_region_size
        target_x = relative_x * new_width + new_offset_x - widget_x
        target_y = relative_y * new_height + new_offset_y - widget_y
        if region_width:
            self._canvas.xview_moveto(max(0.0, min(target_x / region_width, 1.0)))
        if region_height:
            self._canvas.yview_moveto(max(0.0, min(target_y / region_height, 1.0)))

    def _update_zoom_controls(self) -> None:
        self._zoom_label.config(text=f"{round(self._zoom_factor * 100)}%")
        self._zoom_in_button.state(
            ["disabled" if self._zoom_factor >= self._MAX_ZOOM_FACTOR - 1e-6 else "!disabled"]
        )
        self._zoom_out_button.state(
            ["disabled" if self._zoom_factor <= self._MIN_ZOOM_FACTOR + 1e-6 else "!disabled"]
        )

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
