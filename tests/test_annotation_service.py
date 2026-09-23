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


def test_marker_stroke_accumulates_points_in_order():
    from presentation.screens.reader_screen import MarkerStroke

    stroke = MarkerStroke(color="#ffeb3b", alpha=0.35)
    stroke.add_point(10, 20)
    stroke.add_point(15, 25)
    stroke.add_point(20, 30)

    assert stroke.points == [(10, 20), (15, 25), (20, 30)]
    assert stroke.color == "#ffeb3b"
    assert stroke.alpha == 0.35


def test_marker_service_persists_strokes_for_page():
    from application.services.marker_service import MarkerService

    class FakePageMarkerRepository:
        def __init__(self):
            self._data = {}

        def save(self, marker):
            self._data.setdefault(marker.book_id, {}).setdefault(marker.page_number, []).append(marker)
            return marker

        def list_by_book(self, book_id):
            return self._data.get(book_id, {})

        def list_by_page(self, book_id, page_number):
            return self._data.get(book_id, {}).get(page_number, [])

        def delete_page(self, book_id, page_number):
            self._data.get(book_id, {}).pop(page_number, None)

    service = MarkerService(FakePageMarkerRepository())
    service.save_stroke(book_id=7, page_number=2, points=[(1, 2), (3, 4)], color="#ffeb3b", alpha=0.35)

    persisted = service.list_by_page(book_id=7, page_number=2)
    assert len(persisted) == 1
    assert persisted[0].points == [(1, 2), (3, 4)]
    assert persisted[0].color == "#ffeb3b"
    assert persisted[0].alpha == 0.35
