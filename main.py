from __future__ import annotations

import tkinter as tk
from pathlib import Path

from application.services.annotation_service import AnnotationService
from application.services.library_service import LibraryService
from application.services.reading_service import ReadingService
from infrastructure.database import create_connection
from infrastructure.pdf.pymupdf_document import PdfDocument
from infrastructure.repositories.sqlite_annotation_repository import SqliteAnnotationRepository
from infrastructure.repositories.sqlite_book_repository import SqliteBookRepository
from infrastructure.repositories.sqlite_progress_repository import SqliteProgressRepository
from presentation.app import BookerApp

DB_PATH = str(Path.home() / ".booker" / "booker.db")


def main() -> None:
    connection = create_connection(DB_PATH)

    book_repository = SqliteBookRepository(connection)
    annotation_repository = SqliteAnnotationRepository(connection)
    progress_repository = SqliteProgressRepository(connection)

    library_service = LibraryService(book_repository, progress_repository, PdfDocument)
    reading_service = ReadingService(book_repository, progress_repository, PdfDocument)
    annotation_service = AnnotationService(annotation_repository)

    root = tk.Tk()
    root.title("Booker")
    root.geometry("1100x700")

    BookerApp(root, library_service, reading_service, annotation_service)

    root.mainloop()


if __name__ == "__main__":
    main()
