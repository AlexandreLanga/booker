from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BookSummary:
    id: int
    title: str
    file_path: str
    total_pages: int
    progress_percentage: float


@dataclass(frozen=True)
class AnnotationView:
    id: int
    page_number: int
    content: str
