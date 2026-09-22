from __future__ import annotations

import pymupdf

from domain.value_objects import SearchResult


class PdfDocument:
    """Thin wrapper around PyMuPDF for rendering pages and searching text."""

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._doc = pymupdf.open(file_path)

    @property
    def page_count(self) -> int:
        return self._doc.page_count

    def render_page(self, page_number: int, zoom: float = 1.5) -> bytes:
        page = self._doc.load_page(page_number)
        matrix = pymupdf.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)
        return pixmap.tobytes("ppm")

    def search(self, query: str) -> list[SearchResult]:
        if not query.strip():
            return []
        results: list[SearchResult] = []
        for page_number in range(self._doc.page_count):
            page = self._doc.load_page(page_number)
            matches = page.search_for(query)
            if matches:
                snippet = self._extract_snippet(page, query)
                results.append(SearchResult(page_number=page_number, snippet=snippet))
        return results

    @staticmethod
    def _extract_snippet(page, query: str, context: int = 40) -> str:
        text = page.get_text()
        lower_text = text.lower()
        index = lower_text.find(query.lower())
        if index == -1:
            return query
        start = max(0, index - context)
        end = min(len(text), index + len(query) + context)
        return text[start:end].replace("\n", " ").strip()

    def close(self) -> None:
        self._doc.close()
