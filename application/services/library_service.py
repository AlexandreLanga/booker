from __future__ import annotations

import os
from datetime import datetime
from typing import Callable

from application.dto import BookSummary
from domain.entities import Book
from domain.exceptions import BookNotFoundError, InvalidPdfError
from domain.repositories import BookRepository, ReadingProgressRepository


class LibraryService:
    """Coordinates importing and listing books in the user's library."""

    def __init__(
        self,
        book_repository: BookRepository,
        progress_repository: ReadingProgressRepository,
        pdf_document_factory: Callable[[str], object],
    ):
        self._book_repository = book_repository
        self._progress_repository = progress_repository
        self._pdf_document_factory = pdf_document_factory

    def import_book(self, file_path: str) -> Book:
        existing = self._book_repository.get_by_path(file_path)
        if existing:
            return existing

        try:
            document = self._pdf_document_factory(file_path)
        except Exception as error:
            raise InvalidPdfError(f"Não foi possível abrir o arquivo PDF: {file_path}") from error

        try:
            total_pages = document.page_count
        finally:
            document.close()

        title = os.path.splitext(os.path.basename(file_path))[0]
        book = Book(id=None, title=title, file_path=file_path, total_pages=total_pages)
        return self._book_repository.add(book)

    def list_books(
        self,
        query: str = "",
        status: str = "Todos",
        favorite_only: bool = False,
        sort_by: str = "added_at",
    ) -> list[BookSummary]:
        summaries: list[BookSummary] = []
        for book in self._book_repository.list_all():
            searchable = " ".join((book.title, book.author, book.category, *book.tags)).casefold()
            if query.strip() and query.casefold() not in searchable:
                continue
            if status != "Todos" and book.status != status:
                continue
            if favorite_only and not book.favorite:
                continue
            progress = self._progress_repository.get_by_book(book.id)
            percentage = progress.percentage(book.total_pages) if progress else 0.0
            summaries.append(
                BookSummary(
                    id=book.id,
                    title=book.title,
                    file_path=book.file_path,
                    total_pages=book.total_pages,
                    progress_percentage=percentage,
                    author=book.author,
                    category=book.category,
                    favorite=book.favorite,
                    status=book.status,
                    tags=tuple(book.tags),
                    added_at=book.added_at,
                )
            )

        if sort_by == "added_at":
            summaries.sort(key=lambda item: item.added_at or datetime.min, reverse=True)
            return summaries

        sort_key = {
            "title": lambda item: item.title.casefold(),
            "author": lambda item: item.author.casefold(),
            "progress": lambda item: item.progress_percentage,
            "category": lambda item: item.category.casefold(),
        }.get(sort_by)
        if sort_key is not None:
            summaries.sort(key=sort_key)
        return summaries

    def remove_book(self, book_id: int) -> None:
        if not self._book_repository.get_by_id(book_id):
            raise BookNotFoundError(f"Livro {book_id} não encontrado")
        self._book_repository.delete(book_id)

    def update_metadata(self, book_id: int, **metadata) -> Book:
        book = self._book_repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Livro {book_id} não encontrado")
        for field_name in ("title", "author", "publisher", "isbn", "publication_year", "category", "tags", "favorite", "status"):
            if field_name in metadata:
                setattr(book, field_name, metadata[field_name])
        return self._book_repository.update(book)
