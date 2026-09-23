from __future__ import annotations

import tkinter as tk
from pathlib import Path

from application.services.annotation_service import AnnotationService
from application.services.library_service import LibraryService
from application.services.reading_service import ReadingService
from application.services.marker_service import MarkerService
from infrastructure.database import create_connection
from infrastructure.pdf.pymupdf_document import PdfDocument
from infrastructure.repositories.sqlite_annotation_repository import SqliteAnnotationRepository
from infrastructure.repositories.sqlite_book_repository import SqliteBookRepository
from infrastructure.repositories.sqlite_marker_repository import SqliteMarkerRepository
from infrastructure.repositories.sqlite_progress_repository import SqliteProgressRepository
from presentation.app import BookerApp
from presentation.theme import BACKGROUND, apply_theme

DB_PATH = str(Path.home() / ".booker" / "booker.db")


def main() -> None:
    connection = create_connection(DB_PATH)

    book_repository = SqliteBookRepository(connection)
    annotation_repository = SqliteAnnotationRepository(connection)
    progress_repository = SqliteProgressRepository(connection)
    marker_repository = SqliteMarkerRepository(connection)

    library_service = LibraryService(book_repository, progress_repository, PdfDocument)
    reading_service = ReadingService(book_repository, progress_repository, PdfDocument)
    annotation_service = AnnotationService(annotation_repository)
    marker_service = MarkerService(marker_repository)

    root = tk.Tk()
    root.title("Booker")
    root.geometry("1200x760")
    root.minsize(900, 600)
    root.configure(background=BACKGROUND)
    apply_theme(root)

    BookerApp(root, library_service, reading_service, annotation_service, marker_service=marker_service)

    root.mainloop()


if __name__ == "__main__":
    main()
