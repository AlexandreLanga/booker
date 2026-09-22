from __future__ import annotations

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
    ):
        super().__init__(master, style="TFrame")
        self._on_import = on_import
        self._on_open_book = on_open_book
        self._on_delete_book = on_delete_book

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
        ttk.Button(
            actions, text="＋  Importar PDF", style="Accent.TButton", command=self._handle_import
        ).pack(side="right", padx=(0, 8))

        card = ttk.Frame(self, style="Card.TFrame", borderwidth=1, relief="solid")
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        columns = ("title", "pages", "progress")
        self._tree = ttk.Treeview(card, columns=columns, show="headings", selectmode="browse", height=14)
        self._tree.heading("title", text="TÍTULO")
        self._tree.heading("pages", text="PÁGINAS")
        self._tree.heading("progress", text="PROGRESSO")
        self._tree.column("title", width=440, anchor="w")
        self._tree.column("pages", width=110, anchor="center")
        self._tree.column("progress", width=140, anchor="center")
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
        self._tree.delete(*self._tree.get_children())
        if not books:
            self._tree.insert(
                "",
                "end",
                values=("Nenhum livro importado ainda. Clique em “Importar PDF” para começar.", "", ""),
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
                values=(book.title, book.total_pages, f"{book.progress_percentage}%"),
                tags=(tag,),
            )
        suffix = "livro" if len(books) == 1 else "livros"
        self._status_label.config(text=f"{len(books)} {suffix} na biblioteca")

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
        if selection and selection[0].isdigit():
            self._on_open_book(int(selection[0]))

    def _handle_delete(self) -> None:
        selection = self._tree.selection()
        if selection and selection[0].isdigit():
            self._on_delete_book(int(selection[0]))
