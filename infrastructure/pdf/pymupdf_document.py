from __future__ import annotations

import logging
import shutil
import threading
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable

import pymupdf

from domain.value_objects import SearchResult

logger = logging.getLogger(__name__)


class PdfDocument:
    """Thin wrapper around PyMuPDF for rendering pages and searching text."""

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._doc = self._open_document(file_path)
        self._ocr_available: bool | None = None
        self._ocr_text_cache: dict[int, str | None] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _open_document(file_path: str):
        suffix = Path(file_path).suffix.casefold()
        if suffix == ".pdf":
            return pymupdf.open(file_path)
        if suffix == ".txt":
            content = Path(file_path).read_text(encoding="utf-8-sig", errors="replace")
        elif suffix == ".epub":
            content = PdfDocument._read_epub_text(file_path)
        else:
            raise ValueError(f"Formato não suportado: {suffix or 'desconhecido'}")
        return PdfDocument._document_from_text(content)

    @staticmethod
    def _document_from_text(content: str):
        document = pymupdf.open()
        chunks = [content[index : index + 3000] for index in range(0, len(content), 3000)] or [""]
        for chunk in chunks:
            page = document.new_page(width=595, height=842)
            page.insert_textbox(pymupdf.Rect(55, 55, 540, 790), chunk, fontsize=11, lineheight=1.3)
        return document

    @staticmethod
    def _read_epub_text(file_path: str) -> str:
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.parts: list[str] = []

            def handle_data(self, data: str) -> None:
                text = " ".join(data.split())
                if text:
                    self.parts.append(text)

        extractor = TextExtractor()
        with zipfile.ZipFile(file_path) as archive:
            names = sorted(
                name for name in archive.namelist() if Path(name).suffix.casefold() in {".html", ".xhtml", ".htm"}
            )
            for name in names:
                extractor.feed(archive.read(name).decode("utf-8", errors="replace"))
                extractor.parts.append("\n")
        return "\n".join(extractor.parts)

    @property
    def page_count(self) -> int:
        return self._doc.page_count

    def render_page(self, page_number: int, zoom: float = 1.5) -> bytes:
        with self._lock:
            page = self._doc.load_page(page_number)
            matrix = pymupdf.Matrix(zoom, zoom)
            pixmap = page.get_pixmap(matrix=matrix)
            return pixmap.tobytes("ppm")

    def search(
        self,
        query: str,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[SearchResult]:
        query = query.strip()
        if not query:
            return []
        with self._lock:
            results: list[SearchResult] = []
            for page_number in range(self._doc.page_count):
                page = self._doc.load_page(page_number)
                try:
                    text = page.get_text()
                    matches = page.search_for(query)
                    text_source = text

                    if self._text_looks_corrupted(text) or not matches:
                        if page_number not in self._ocr_text_cache:
                            self._ocr_text_cache[page_number] = self._extract_ocr_text(page)
                        ocr_text = self._ocr_text_cache[page_number]
                        if ocr_text is not None and query.casefold() in ocr_text.casefold():
                            matches = [query]
                            text_source = ocr_text

                    if matches:
                        snippet = self._extract_snippet(text_source, query)
                        results.append(SearchResult(page_number=page_number, snippet=snippet))
                except Exception:
                    logger.exception("Falha ao pesquisar no PDF %s, página %s", self._file_path, page_number + 1)
                if progress_callback is not None:
                    progress_callback(page_number + 1, self._doc.page_count)
            return results

    @staticmethod
    def _extract_snippet(text: str, query: str, context: int = 40) -> str:
        lower_text = text.lower()
        index = lower_text.find(query.lower())
        if index == -1:
            return query
        start = max(0, index - context)
        end = min(len(text), index + len(query) + context)
        return text[start:end].replace("\n", " ").strip()

    @staticmethod
    def _text_looks_corrupted(text: str) -> bool:
        if not text.strip():
            return True
        suspicious = sum(
            1
            for character in text
            if character == "\ufffd" or unicodedata.category(character) in {"Cc", "Cf", "Co"}
        )
        return suspicious > max(2, len(text) // 100)

    def _extract_ocr_text(self, page) -> str | None:
        if self._ocr_available is False:
            return None
        try:
            language, tessdata = self._ocr_configuration()
            ocr_options = {"language": language, "dpi": 150, "full": True}
            if tessdata is not None:
                ocr_options["tessdata"] = tessdata
            ocr_options["dpi"] = 100
            text_page = page.get_textpage_ocr(**ocr_options)
            self._ocr_available = True
            return text_page.extractText()
        except Exception as error:
            self._ocr_available = False
            logger.warning(
                "OCR desabilitado para o PDF %s: %s. Instale o Tesseract com os idiomas por e eng "
                "para pesquisar texto corrompido ou escaneado.",
                self._file_path,
                error,
            )
            return None

    @staticmethod
    def _ocr_configuration() -> tuple[str, str | None]:
        executable = shutil.which("tesseract")
        if executable is None:
            for candidate in (
                Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
                Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
            ):
                if candidate.exists():
                    executable = str(candidate)
                    break

        tessdata_path = Path(executable).parent / "tessdata" if executable else None
        languages = [
            language
            for language in ("por", "eng")
            if tessdata_path is not None and (tessdata_path / f"{language}.traineddata").exists()
        ]
        if not languages:
            languages = ["por+eng"]
        return "+".join(languages), str(tessdata_path) if tessdata_path is not None else None

    def close(self) -> None:
        with self._lock:
            self._doc.close()
