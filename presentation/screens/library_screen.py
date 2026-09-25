from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from application.dto import BookSummary
from presentation.theme import SURFACE, SURFACE_ALT


class LibraryScreen(ttk.Frame):
    """Displays the user's book library and allows importing new PDFs."""

    def __init__(
        self,
        master,
        on_import: Callable[[str], None],
        on_open_book: Callable[[int], None],
        on_delete_book: Callable[[int], None],
        on_edit_book: Callable[[int, dict], None],
        on_filter: Callable[[str, str, bool, str], None],
    ):
        super().__init__(master, style="TFrame")
        self._on_import = on_import
        self._on_open_book = on_open_book
        self._on_delete_book = on_delete_book
        self._on_edit_book = on_edit_book
        self._on_filter = on_filter
        self._books_by_id: dict[int, BookSummary] = {}

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self) -> None:
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=28, pady=(24, 12))

        title_box = ttk.Frame(header, style="TFrame")
        title_box.pack(side="left")
        ttk.Label(title_box, text="📚 Minha Biblioteca", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            title_box,
            text="Importe seus PDFs e continue de onde parou",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        actions = ttk.Frame(header, style="TFrame")
        actions.pack(side="right")
        ttk.Button(actions, text="🗑  Remover", style="Danger.TButton", command=self._handle_delete).pack(
            side="right"
        )
        ttk.Button(actions, text="✎  Editar", command=self._handle_edit).pack(side="right", padx=(0, 8))
        ttk.Button(
            actions, text="＋  Importar PDF", style="Accent.TButton", command=self._handle_import
        ).pack(side="right", padx=(0, 8))

        filters = ttk.Frame(self, style="TFrame")
        filters.pack(fill="x", padx=28, pady=(0, 10))

        ttk.Label(filters, text="Filtrar:", style="MutedOnBg.TLabel").pack(side="left")
        self._filter_query = tk.StringVar()
        search = ttk.Entry(filters, textvariable=self._filter_query, width=28)
        search.pack(side="left", padx=(8, 10))
        search.bind("<Return>", lambda _event: self._apply_filters())
        ttk.Button(filters, text="🔍 Filtrar", command=self._apply_filters).pack(side="left", padx=(0, 12))

        self._filter_status = tk.StringVar(value="Todos")
        ttk.Combobox(
            filters,
            textvariable=self._filter_status,
            values=("Todos", "Não iniciado", "Lendo", "Pausado", "Concluído", "Abandonado"),
            state="readonly",
            width=15,
        ).pack(side="left")

        self._filter_favorite = tk.BooleanVar(value=False)
        ttk.Checkbutton(filters, text="Favoritos", variable=self._filter_favorite, command=self._apply_filters).pack(
            side="left", padx=(12, 0)
        )

        self._sort_value_to_label = {
            "added_at": "Mais recentes",
            "title": "Título",
            "author": "Autor",
            "category": "Categoria",
            "progress": "Progresso",
        }
        self._sort_label_to_value = {label: value for value, label in self._sort_value_to_label.items()}
        self._filter_sort = tk.StringVar(value=self._sort_value_to_label["added_at"])
        self._sort_combo = ttk.Combobox(
            filters,
            textvariable=self._filter_sort,
            values=list(self._sort_value_to_label.values()),
            state="readonly",
            width=16,
            justify="center",
        )
        self._sort_combo.pack(side="right")
        ttk.Label(filters, text="Ordenar por:", style="MutedOnBg.TLabel").pack(side="right", padx=(0, 8))

        stats = ttk.Frame(self, style="TFrame")
        stats.pack(fill="x", padx=28, pady=(0, 12))
        self._stats_total = ttk.Label(stats, text="Total: 0", style="MutedOnBg.TLabel")
        self._stats_total.pack(side="left")
        self._stats_reading = ttk.Label(stats, text="Lendo: 0", style="MutedOnBg.TLabel")
        self._stats_reading.pack(side="left", padx=(18, 0))
        self._stats_favorites = ttk.Label(stats, text="Favoritos: 0", style="MutedOnBg.TLabel")
        self._stats_favorites.pack(side="left", padx=(18, 0))

        card = ttk.Frame(self, style="Card.TFrame", borderwidth=1, relief="solid")
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        columns = ("title", "author", "category", "status", "favorite", "pages", "progress")
        self._tree = ttk.Treeview(card, columns=columns, show="headings", selectmode="browse", height=14)
        self._tree.heading("title", text="TÍTULO", anchor="w")
        self._tree.heading("author", text="AUTOR", anchor="w")
        self._tree.heading("category", text="CATEGORIA", anchor="w")
        self._tree.heading("status", text="STATUS", anchor="center")
        self._tree.heading("favorite", text="★", anchor="center")
        self._tree.heading("pages", text="PÁGINAS", anchor="center")
        self._tree.heading("progress", text="PROGRESSO", anchor="center")
        self._tree.column("title", width=320, minwidth=220, stretch=True, anchor="w")
        self._tree.column("author", width=180, minwidth=120, stretch=True, anchor="w")
        self._tree.column("category", width=150, minwidth=100, stretch=True, anchor="w")
        self._tree.column("status", width=130, minwidth=110, stretch=False, anchor="center")
        self._tree.column("favorite", width=52, minwidth=40, stretch=False, anchor="center")
        self._tree.column("pages", width=90, minwidth=80, stretch=False, anchor="center")
        self._tree.column("progress", width=120, minwidth=100, stretch=False, anchor="center")
        self._tree.tag_configure("odd", background=SURFACE)
        self._tree.tag_configure("even", background=SURFACE_ALT)
        self._tree.tag_configure("empty", foreground="#9aa0ac")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side="left", fill="both", expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side="right", fill="y", pady=1)

        self._status_label = ttk.Label(self, text="", style="MutedOnBg.TLabel")
        self._status_label.pack(fill="x", padx=32, pady=(0, 16))

    def _bind_events(self) -> None:
        self._tree.bind("<Double-1>", lambda _event: self._handle_open())

    def show_books(self, books: list[BookSummary]) -> None:
        self._books_by_id = {book.id: book for book in books}
        self._tree.delete(*self._tree.get_children())
        total = len(books)
        reading = sum(1 for book in books if book.status == "Lendo")
        favorites = sum(1 for book in books if book.favorite)
        self._stats_total.config(text=f"Total: {total}")
        self._stats_reading.config(text=f"Lendo: {reading}")
        self._stats_favorites.config(text=f"Favoritos: {favorites}")

        if not books:
            self._tree.insert(
                "",
                "end",
                values=("Nenhum livro importado ainda. Clique em “Importar PDF” para começar.", "", "", "", "", "", ""),
                tags=("empty",),
            )
            self._status_label.config(text="")
            return

        for index, book in enumerate(books):
            tag = "even" if index % 2 == 0 else "odd"
            self._tree.insert(
                "",
                "end",
                iid=str(book.id),
                values=(book.title, book.author, book.category, book.status, "★" if book.favorite else "", book.total_pages, f"{book.progress_percentage}%"),
                tags=(tag,),
            )
        suffix = "livro" if len(books) == 1 else "livros"
        self._status_label.config(text=f"{len(books)} {suffix} na biblioteca")

    def show_error(self, message: str) -> None:
        messagebox.showerror("Erro", message)

    def _handle_import(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Selecione um livro",
            filetypes=[("Livros", "*.pdf *.epub *.txt"), ("PDF", "*.pdf"), ("EPUB", "*.epub"), ("Texto", "*.txt")],
        )
        if file_path:
            self._on_import(file_path)

    def _handle_open(self) -> None:
        selection = self._tree.selection()
        if selection and selection[0].isdigit():
            self._on_open_book(int(selection[0]))

    def _handle_delete(self) -> None:
        selection = self._tree.selection()
        if selection and selection[0].isdigit():
            self._on_delete_book(int(selection[0]))

    def _apply_filters(self) -> None:
        sort_value = self._sort_label_to_value.get(self._filter_sort.get(), "added_at")
        self._on_filter(
            self._filter_query.get(),
            self._filter_status.get(),
            self._filter_favorite.get(),
            sort_value,
        )

    def _handle_edit(self) -> None:
        selection = self._tree.selection()
        if not selection or not selection[0].isdigit():
            return
        book = self._books_by_id.get(int(selection[0]))
        if book is None:
            return
        window = tk.Toplevel(self)
        window.title("Editar livro")
        window.transient(self.winfo_toplevel())
        window.grab_set()

        form = ttk.Frame(window, padding=16)
        form.pack(fill="both", expand=True)
        fields = (("Título", "title", book.title), ("Autor", "author", book.author), ("Categoria", "category", book.category))
        variables: dict[str, tk.StringVar] = {}
        for row, (label, name, value) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
            variable = tk.StringVar(value=value)
            variables[name] = variable
            ttk.Entry(form, textvariable=variable, width=36).grid(row=row, column=1, sticky="ew", pady=5)

        ttk.Label(form, text="Status").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
        status = tk.StringVar(value=book.status)
        ttk.Combobox(
            form,
            textvariable=status,
            values=("Não iniciado", "Lendo", "Pausado", "Concluído", "Abandonado"),
            state="readonly",
            width=33,
        ).grid(row=3, column=1, sticky="ew", pady=5)
        favorite = tk.BooleanVar(value=book.favorite)
        ttk.Checkbutton(form, text="Favorito", variable=favorite).grid(row=4, column=1, sticky="w", pady=5)
        form.columnconfigure(1, weight=1)

        def save() -> None:
            self._on_edit_book(
                book.id,
                {
                    "title": variables["title"].get().strip() or book.title,
                    "author": variables["author"].get().strip(),
                    "category": variables["category"].get().strip(),
                    "status": status.get(),
                    "favorite": favorite.get(),
                },
            )
            window.destroy()

        buttons = ttk.Frame(form)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancelar", command=window.destroy).pack(side="right")
        ttk.Button(buttons, text="Salvar", style="Accent.TButton", command=save).pack(side="right", padx=(0, 8))
