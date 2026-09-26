import threading

from infrastructure.pdf.pymupdf_document import PdfDocument


class FakePage:
    def get_text(self):
        return "texto da página"

    def search_for(self, query):
        return []


class FakeDocument:
    page_count = 2

    def load_page(self, page_number):
        return FakePage()


class SlowPage(FakePage):
    def __init__(self, started, release):
        self._started = started
        self._release = release

    def get_text(self):
        self._started.set()
        self._release.wait(timeout=1)
        return super().get_text()


class SlowDocument:
    page_count = 1

    def __init__(self, started, release):
        self._page = SlowPage(started, release)

    def load_page(self, page_number):
        return self._page

    def close(self):
        pass


def test_search_does_not_hold_render_lock_during_slow_page():
    document = PdfDocument.__new__(PdfDocument)
    document._file_path = "sample.pdf"
    document._doc = FakeDocument()
    search_started = threading.Event()
    release_search = threading.Event()
    document._search_doc = SlowDocument(search_started, release_search)
    document._ocr_available = False
    document._ocr_text_cache = {}
    document._lock = threading.RLock()
    document._search_lock = threading.RLock()

    search_thread = threading.Thread(target=document.search, args=("termo",))
    search_thread.start()
    assert search_started.wait(timeout=1)

    render_lock_acquired = threading.Event()
    render_thread = threading.Thread(
        target=lambda: _acquire_lock(document, render_lock_acquired),
    )
    render_thread.start()
    assert render_lock_acquired.wait(timeout=1)

    release_search.set()
    search_thread.join(timeout=1)
    render_thread.join(timeout=1)
    assert not search_thread.is_alive()
    assert not render_thread.is_alive()


def _acquire_lock(document, acquired):
    with document._lock:
        acquired.set()