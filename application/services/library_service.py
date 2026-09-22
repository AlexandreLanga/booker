from __future__ import annotations

import os
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

    def list_books(self) -> list[BookSummary]:
        summaries: list[BookSummary] = []
        for book in self._book_repository.list_all():
            progress = self._progress_repository.get_by_book(book.id)
            percentage = progress.percentage(book.total_pages) if progress else 0.0
            summaries.append(
                BookSummary(
                    id=book.id,
                    title=book.title,
                    file_path=book.file_path,
                    total_pages=book.total_pages,
                    progress_percentage=percentage,
                )
            )
        return summaries

    def remove_book(self, book_id: int) -> None:
        if not self._book_repository.get_by_id(book_id):
            raise BookNotFoundError(f"Livro {book_id} não encontrado")
        self._book_repository.delete(book_id)
