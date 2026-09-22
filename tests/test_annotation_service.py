import pytest

from application.services.annotation_service import AnnotationService


class FakeAnnotationRepository:
    def __init__(self):
        self._annotations = {}
        self._next_id = 1

    def add(self, annotation):
        annotation.id = self._next_id
        self._annotations[annotation.id] = annotation
        self._next_id += 1
        return annotation

    def list_by_book(self, book_id):
        return [a for a in self._annotations.values() if a.book_id == book_id]

    def list_by_page(self, book_id, page_number):
        return [
            a for a in self._annotations.values() if a.book_id == book_id and a.page_number == page_number
        ]

    def delete(self, annotation_id):
        self._annotations.pop(annotation_id, None)


def test_add_annotation_creates_view():
    service = AnnotationService(FakeAnnotationRepository())

    view = service.add_annotation(book_id=1, page_number=2, content="  nota importante  ")

    assert view.id == 1
    assert view.page_number == 2
    assert view.content == "nota importante"


def test_add_annotation_rejects_empty_content():
    service = AnnotationService(FakeAnnotationRepository())

    with pytest.raises(ValueError):
        service.add_annotation(book_id=1, page_number=0, content="   ")


def test_delete_annotation_removes_it_from_list():
    repository = FakeAnnotationRepository()
    service = AnnotationService(repository)
    view = service.add_annotation(book_id=1, page_number=0, content="nota")

    service.delete_annotation(view.id)

    assert service.list_by_book(1) == []
