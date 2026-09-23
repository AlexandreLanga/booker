from __future__ import annotations

from domain.entities import PageMarker


class MarkerService:
    """Stores transparent colored marks per page and book."""

    def __init__(self, marker_repository):
        self._marker_repository = marker_repository

    def save_stroke(self, book_id: int, page_number: int, points: list[tuple[float, float]], color: str, alpha: float) -> PageMarker:
        marker = PageMarker(
            id=None,
            book_id=book_id,
            page_number=page_number,
            points=list(points),
            color=color,
            alpha=float(alpha),
        )
        return self._marker_repository.save(marker)

    def list_by_page(self, book_id: int, page_number: int) -> list[PageMarker]:
        return self._marker_repository.list_by_page(book_id, page_number)

    def list_by_book(self, book_id: int) -> dict[int, list[PageMarker]]:
        return self._marker_repository.list_by_book(book_id)

    def clear_page(self, book_id: int, page_number: int) -> None:
        self._marker_repository.delete_page(book_id, page_number)
