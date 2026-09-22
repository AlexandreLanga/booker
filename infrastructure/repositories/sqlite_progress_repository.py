from __future__ import annotations

import sqlite3
from datetime import datetime

from domain.entities import ReadingProgress


class SqliteProgressRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def get_by_book(self, book_id: int) -> ReadingProgress | None:
        row = self._connection.execute(
            "SELECT book_id, current_page, last_read_at FROM reading_progress WHERE book_id = ?",
            (book_id,),
        ).fetchone()
        if not row:
            return None
        return ReadingProgress(book_id=row[0], current_page=row[1], last_read_at=datetime.fromisoformat(row[2]))

    def save(self, progress: ReadingProgress) -> None:
        self._connection.execute(
            "INSERT INTO reading_progress (book_id, current_page, last_read_at) VALUES (?, ?, ?) "
            "ON CONFLICT(book_id) DO UPDATE SET current_page = excluded.current_page, "
            "last_read_at = excluded.last_read_at",
            (progress.book_id, progress.current_page, progress.last_read_at.isoformat()),
        )
        self._connection.commit()
