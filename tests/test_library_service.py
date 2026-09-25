import pytest

from application.services.library_service import LibraryService
from domain.entities import ReadingProgress
from domain.exceptions import BookNotFoundError, InvalidPdfError


class FakeBookRepository:
    def __init__(self):
        self._books = {}
        self._next_id = 1

    def add(self, book):
        book.id = self._next_id
        self._books[book.id] = book
        self._next_id += 1
        return book

    def get_by_id(self, book_id):
        return self._books.get(book_id)

    def get_by_path(self, file_path):
        return next((b for b in self._books.values() if b.file_path == file_path), None)

    def list_all(self):
        return list(self._books.values())

    def delete(self, book_id):
        self._books.pop(book_id, None)


class FakeProgressRepository:
    def __init__(self):
        self._progress = {}

    def get_by_book(self, book_id):
        return self._progress.get(book_id)

    def save(self, progress):
        self._progress[progress.book_id] = progress


class FakePdfDocument:
    def __init__(self, file_path, page_count=10):
        self.file_path = file_path
        self.page_count = page_count
        self.closed = False

    def close(self):
        self.closed = True


def make_fake_document(file_path):
    return FakePdfDocument(file_path)


def failing_document_factory(file_path):
    raise RuntimeError("corrupted file")


def test_import_book_creates_new_book():
    service = LibraryService(FakeBookRepository(), FakeProgressRepository(), make_fake_document)

    book = service.import_book("sample.pdf")

    assert book.id == 1
    assert book.title == "sample"
    assert book.total_pages == 10


def test_import_book_returns_existing_book_when_already_imported():
    book_repository = FakeBookRepository()
    service = LibraryService(book_repository, FakeProgressRepository(), make_fake_document)

    first = service.import_book("sample.pdf")
    second = service.import_book("sample.pdf")

    assert first.id == second.id
    assert len(book_repository.list_all()) == 1


def test_import_book_raises_invalid_pdf_error_on_broken_file():
    service = LibraryService(FakeBookRepository(), FakeProgressRepository(), failing_document_factory)

    with pytest.raises(InvalidPdfError):
        service.import_book("broken.pdf")


def test_list_books_includes_progress_percentage():
    book_repository = FakeBookRepository()
    progress_repository = FakeProgressRepository()
    service = LibraryService(book_repository, progress_repository, make_fake_document)
    book = service.import_book("sample.pdf")
    progress_repository.save(ReadingProgress(book_id=book.id, current_page=4))

    summaries = service.list_books()

    assert summaries[0].progress_percentage == 50.0


def test_remove_book_raises_when_not_found():
    service = LibraryService(FakeBookRepository(), FakeProgressRepository(), make_fake_document)

    with pytest.raises(BookNotFoundError):
        service.remove_book(999)


def test_list_books_filters_and_sorts_metadata():
    book_repository = FakeBookRepository()
    progress_repository = FakeProgressRepository()
    service = LibraryService(book_repository, progress_repository, make_fake_document)
    first = service.import_book("first.pdf")
    second = service.import_book("second.pdf")
    first.author = "Machado de Assis"
    first.status = "Lendo"
    first.favorite = True
    second.author = "Jose de Alencar"
    second.status = "Concluído"
    book_repository._books[first.id] = first
    book_repository._books[second.id] = second
    progress_repository.save(ReadingProgress(book_id=first.id, current_page=2))
    progress_repository.save(ReadingProgress(book_id=second.id, current_page=9))

    results = service.list_books(query="machado", status="Lendo", favorite_only=True)
    assert [book.id for book in results] == [first.id]

    ordered = service.list_books(sort_by="progress")
    assert [book.id for book in ordered] == [first.id, second.id]


def test_list_books_sorts_by_most_recent_added_at():
    from datetime import datetime, timedelta

    book_repository = FakeBookRepository()
    progress_repository = FakeProgressRepository()
    service = LibraryService(book_repository, progress_repository, make_fake_document)

    older = service.import_book("older.pdf")
    newer = service.import_book("newer.pdf")
    older.added_at = datetime.now() - timedelta(days=10)
    newer.added_at = datetime.now()
    book_repository._books[older.id] = older
    book_repository._books[newer.id] = newer

    ordered = service.list_books(sort_by="added_at")

    assert [book.id for book in ordered] == [newer.id, older.id]
