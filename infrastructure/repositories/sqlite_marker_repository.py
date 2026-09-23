from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from domain.entities import PageMarker


class SqliteMarkerRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def save(self, marker: PageMarker) -> PageMarker:
        cursor = self._connection.execute(
            "INSERT INTO page_markers (book_id, page_number, points, color, alpha, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                marker.book_id,
                marker.page_number,
                json.dumps(marker.points),
                marker.color,
                marker.alpha,
                marker.created_at.isoformat(),
            ),
        )
        self._connection.commit()
        marker.id = cursor.lastrowid
        return marker

    def list_by_book(self, book_id: int) -> dict[int, list[PageMarker]]:
        rows = self._connection.execute(
            "SELECT id, book_id, page_number, points, color, alpha, created_at FROM page_markers "
            "WHERE book_id = ? ORDER BY page_number ASC, created_at ASC",
            (book_id,),
        ).fetchall()
        result: dict[int, list[PageMarker]] = {}
        for row in rows:
            marker = self._to_entity(row)
            result.setdefault(marker.page_number, []).append(marker)
        return result

    def list_by_page(self, book_id: int, page_number: int) -> list[PageMarker]:
        rows = self._connection.execute(
            "SELECT id, book_id, page_number, points, color, alpha, created_at FROM page_markers "
            "WHERE book_id = ? AND page_number = ? ORDER BY created_at ASC",
            (book_id, page_number),
        ).fetchall()
        return [self._to_entity(row) for row in rows]

    def delete_page(self, book_id: int, page_number: int) -> None:
        self._connection.execute(
            "DELETE FROM page_markers WHERE book_id = ? AND page_number = ?",
            (book_id, page_number),
        )
        self._connection.commit()

    @staticmethod
    def _to_entity(row: tuple) -> PageMarker:
        return PageMarker(
            id=row[0],
            book_id=row[1],
            page_number=row[2],
            points=[tuple(point) for point in json.loads(row[3])],
            color=row[4],
            alpha=row[5],
            created_at=datetime.fromisoformat(row[6]),
        )
