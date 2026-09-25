from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BookSummary:
    id: int
    title: str
    file_path: str
    total_pages: int
    progress_percentage: float
    author: str = ""
    category: str = ""
    favorite: bool = False
    status: str = "Não iniciado"
    tags: tuple[str, ...] = ()
    added_at: datetime | None = None


@dataclass(frozen=True)
class AnnotationView:
    id: int
    page_number: int
    content: str
