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
WINDOW_ICON_PNG = (
    "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"
)
WINDOW_ICON_PNG = WINDOW_ICON_PNG[:1575] + "2" + WINDOW_ICON_PNG[1575:]


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
    assets_path = Path(__file__).resolve().parent / "assets"
    icon_path = assets_path / "booker_logo.ico"
    try:
        root.iconbitmap(str(icon_path))
    except tk.TclError:
        root._icon_image = tk.PhotoImage(data=WINDOW_ICON_PNG)
        root.iconphoto(True, root._icon_image)
    root.geometry("1200x760")
    root.minsize(900, 600)
    root.configure(background=BACKGROUND)
    apply_theme(root)

    BookerApp(root, library_service, reading_service, annotation_service, marker_service=marker_service)

    root.mainloop()


if __name__ == "__main__":
    main()
