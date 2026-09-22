from __future__ import annotations

from typing import Callable

from domain.entities import ReadingProgress
from domain.exceptions import BookNotFoundError
from domain.repositories import BookRepository, ReadingProgressRepository
from domain.value_objects import SearchResult


class ReadingService:
    """Handles opening a book for reading, page navigation and text search."""

    def __init__(
        self,
        book_repository: BookRepository,
        progress_repository: ReadingProgressRepository,
        pdf_document_factory: Callable[[str], object],
    ):
        self._book_repository = book_repository
        self._progress_repository = progress_repository
        self._pdf_document_factory = pdf_document_factory

    def open_book(self, book_id: int):
        book = self._book_repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Livro {book_id} não encontrado")
        document = self._pdf_document_factory(book.file_path)
        progress = self._progress_repository.get_by_book(book_id)
        current_page = progress.current_page if progress else 0
        return book, document, current_page

    def update_progress(self, book_id: int, current_page: int) -> None:
        self._progress_repository.save(ReadingProgress(book_id=book_id, current_page=current_page))

    def search(self, document, query: str) -> list[SearchResult]:
        return document.search(query)
