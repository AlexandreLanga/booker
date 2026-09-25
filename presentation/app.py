from __future__ import annotations

from typing import Callable
import tkinter as tk
from tkinter import ttk

from application.services.annotation_service import AnnotationService
from application.services.library_service import LibraryService
from application.services.marker_service import MarkerService
from application.services.reading_service import ReadingService
from domain.exceptions import DomainError
from presentation.screens.library_screen import LibraryScreen
from presentation.screens.reader_screen import MarkerStroke, ReaderScreen


class BookerApp:
    """Composition root: wires application services to screens and manages navigation."""

    def __init__(
        self,
        root: tk.Tk,
        library_service: LibraryService,
        reading_service: ReadingService,
        annotation_service: AnnotationService,
        marker_service: MarkerService | None = None,
    ):
        self._library_service = library_service
        self._reading_service = reading_service
        self._annotation_service = annotation_service
        self._marker_service = marker_service

        self._current_document = None
        self._current_book_id: int | None = None

        self._container = ttk.Frame(root)
        self._container.pack(fill="both", expand=True)

        self._library_screen = LibraryScreen(
            self._container,
            on_import=self._handle_import,
            on_open_book=self._handle_open_book,
            on_delete_book=self._handle_delete_book,
        )
        self._reader_screen = ReaderScreen(
            self._container,
            on_back=self._show_library,
            on_page_changed=self._handle_page_changed,
            on_search=self._handle_search,
            on_add_annotation=self._handle_add_annotation,
            on_delete_annotation=self._handle_delete_annotation,
        )
        if self._marker_service is not None:
            self._reader_screen._on_save_marker = self._handle_save_markers

        self._show_library()

    def _show_library(self) -> None:
        if self._current_document is not None:
            self._current_document.close()
            self._current_document = None
        self._reader_screen.pack_forget()
        self._library_screen.pack(fill="both", expand=True)
        self._refresh_library()

    def _show_reader(self) -> None:
        self._library_screen.pack_forget()
        self._reader_screen.pack(fill="both", expand=True)

    def _refresh_library(self) -> None:
        self._library_screen.show_books(self._library_service.list_books())

    def _handle_import(self, file_path: str) -> None:
        try:
            self._library_service.import_book(file_path)
            self._refresh_library()
        except DomainError as error:
            self._library_screen.show_error(str(error))

    def _handle_delete_book(self, book_id: int) -> None:
        try:
            self._library_service.remove_book(book_id)
            self._refresh_library()
        except DomainError as error:
            self._library_screen.show_error(str(error))

    def _handle_open_book(self, book_id: int) -> None:
        try:
            book, document, current_page = self._reading_service.open_book(book_id)
        except DomainError as error:
            self._library_screen.show_error(str(error))
            return

        self._current_book_id = book_id
        self._current_document = document
        self._show_reader()
        markers = self._marker_service.list_by_book(book_id) if self._marker_service is not None else {}
        page_markers: dict[int, list[MarkerStroke]] = {}
        for page_number, markers_for_page in markers.items():
            page_markers[page_number] = [
                MarkerStroke(points=marker.points, color=marker.color, alpha=marker.alpha)
                for marker in markers_for_page
            ]
        self._reader_screen.load_book(
            title=book.title,
            total_pages=book.total_pages,
            current_page=current_page,
            render_page_callback=self._render_page,
            persisted_markers=page_markers,
        )
        self._reader_screen.show_annotations(self._annotation_service.list_by_book(book_id))

    def _render_page(self, page_number: int, zoom: float) -> bytes:
        return self._current_document.render_page(page_number, zoom)

    def _handle_page_changed(self, page_number: int) -> None:
        if self._current_book_id is None:
            return
        self._reading_service.update_progress(self._current_book_id, page_number)
        self._reader_screen.show_page(page_number)

    def _handle_search(self, query: str, progress_callback: Callable[[int, int], None] | None = None):
        if self._current_document is None:
            return []
        return self._reading_service.search(self._current_document, query, progress_callback=progress_callback)

    def _handle_add_annotation(self, page_number: int, content: str) -> None:
        if self._current_book_id is None:
            return
        try:
            self._annotation_service.add_annotation(self._current_book_id, page_number, content)
            self._reader_screen.show_annotations(self._annotation_service.list_by_book(self._current_book_id))
        except ValueError as error:
            self._reader_screen.show_error(str(error))

    def _handle_delete_annotation(self, annotation_id: int) -> None:
        if self._current_book_id is None:
            return
        self._annotation_service.delete_annotation(annotation_id)
        self._reader_screen.show_annotations(self._annotation_service.list_by_book(self._current_book_id))

    def _handle_save_markers(self, page_number: int, strokes: list[MarkerStroke]) -> None:
        if self._current_book_id is None or self._marker_service is None:
            return
        self._marker_service.clear_page(self._current_book_id, page_number)
        for stroke in strokes:
            self._marker_service.save_stroke(
                self._current_book_id,
                page_number,
                stroke.points,
                stroke.color,
                stroke.alpha,
            )
