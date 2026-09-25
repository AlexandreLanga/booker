from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Book:
    id: int | None
    title: str
    file_path: str
    total_pages: int
    added_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    publisher: str = ""
    isbn: str = ""
    publication_year: int | None = None
    category: str = ""
    tags: list[str] = field(default_factory=list)
    favorite: bool = False
    status: str = "Não iniciado"


@dataclass
class Annotation:
    id: int | None
    book_id: int
    page_number: int
    content: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReadingProgress:
    book_id: int
    current_page: int
    last_read_at: datetime = field(default_factory=datetime.now)

    def percentage(self, total_pages: int) -> float:
        if total_pages <= 0:
            return 0.0
        return round((self.current_page + 1) / total_pages * 100, 1)


@dataclass
class PageMarker:
    id: int | None
    book_id: int
    page_number: int
    points: list[tuple[float, float]]
    color: str
    alpha: float
    created_at: datetime = field(default_factory=datetime.now)
