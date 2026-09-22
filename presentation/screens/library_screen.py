from __future__ import annotations

from tkinter import filedialog, messagebox, ttk
from typing import Callable

from application.dto import BookSummary


class LibraryScreen(ttk.Frame):
    """Displays the user's book library and allows importing new PDFs."""

    def __init__(
        self,
        master,
        on_import: Callable[[str], None],
        on_open_book: Callable[[int], None],
        on_delete_book: Callable[[int], None],
    ):
        super().__init__(master)
        self._on_import = on_import
        self._on_open_book = on_open_book
        self._on_delete_book = on_delete_book

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)

        ttk.Button(toolbar, text="Importar PDF", command=self._handle_import).pack(side="left")
        ttk.Button(toolbar, text="Remover", command=self._handle_delete).pack(side="left", padx=(8, 0))

        columns = ("title", "pages", "progress")
        self._tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self._tree.heading("title", text="Título")
        self._tree.heading("pages", text="Páginas")
        self._tree.heading("progress", text="Progresso")
        self._tree.column("title", width=360)
        self._tree.column("pages", width=80, anchor="center")
        self._tree.column("progress", width=100, anchor="center")
        self._tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _bind_events(self) -> None:
        self._tree.bind("<Double-1>", lambda _event: self._handle_open())

    def show_books(self, books: list[BookSummary]) -> None:
        self._tree.delete(*self._tree.get_children())
        for book in books:
            self._tree.insert(
                "",
                "end",
                iid=str(book.id),
                values=(book.title, book.total_pages, f"{book.progress_percentage}%"),
            )

    def show_error(self, message: str) -> None:
        messagebox.showerror("Erro", message)

    def _handle_import(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf")],
        )
        if file_path:
            self._on_import(file_path)

    def _handle_open(self) -> None:
        selection = self._tree.selection()
        if selection:
            self._on_open_book(int(selection[0]))

    def _handle_delete(self) -> None:
        selection = self._tree.selection()
        if selection:
            self._on_delete_book(int(selection[0]))
