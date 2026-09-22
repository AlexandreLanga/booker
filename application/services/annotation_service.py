from __future__ import annotations

from application.dto import AnnotationView
from domain.entities import Annotation
from domain.repositories import AnnotationRepository


class AnnotationService:
    """Coordinates creating, listing and removing reader annotations."""

    def __init__(self, annotation_repository: AnnotationRepository):
        self._annotation_repository = annotation_repository

    def add_annotation(self, book_id: int, page_number: int, content: str) -> AnnotationView:
        if not content.strip():
            raise ValueError("A anotação não pode estar vazia")
        annotation = self._annotation_repository.add(
            Annotation(id=None, book_id=book_id, page_number=page_number, content=content.strip())
        )
        return AnnotationView(id=annotation.id, page_number=annotation.page_number, content=annotation.content)

    def list_by_book(self, book_id: int) -> list[AnnotationView]:
        return [
            AnnotationView(id=a.id, page_number=a.page_number, content=a.content)
            for a in self._annotation_repository.list_by_book(book_id)
        ]

    def list_by_page(self, book_id: int, page_number: int) -> list[AnnotationView]:
        return [
            AnnotationView(id=a.id, page_number=a.page_number, content=a.content)
            for a in self._annotation_repository.list_by_page(book_id, page_number)
        ]

    def delete_annotation(self, annotation_id: int) -> None:
        self._annotation_repository.delete(annotation_id)
