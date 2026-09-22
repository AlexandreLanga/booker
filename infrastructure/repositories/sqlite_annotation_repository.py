from __future__ import annotations

import sqlite3
from datetime import datetime

from domain.entities import Annotation


class SqliteAnnotationRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def add(self, annotation: Annotation) -> Annotation:
        cursor = self._connection.execute(
            "INSERT INTO annotations (book_id, page_number, content, created_at) VALUES (?, ?, ?, ?)",
            (annotation.book_id, annotation.page_number, annotation.content, annotation.created_at.isoformat()),
        )
        self._connection.commit()
        annotation.id = cursor.lastrowid
        return annotation

    def list_by_book(self, book_id: int) -> list[Annotation]:
        rows = self._connection.execute(
            "SELECT id, book_id, page_number, content, created_at FROM annotations "
            "WHERE book_id = ? ORDER BY page_number ASC, created_at ASC",
            (book_id,),
        ).fetchall()
        return [self._to_entity(row) for row in rows]

    def list_by_page(self, book_id: int, page_number: int) -> list[Annotation]:
        rows = self._connection.execute(
            "SELECT id, book_id, page_number, content, created_at FROM annotations "
            "WHERE book_id = ? AND page_number = ? ORDER BY created_at ASC",
            (book_id, page_number),
        ).fetchall()
        return [self._to_entity(row) for row in rows]

    def delete(self, annotation_id: int) -> None:
        self._connection.execute("DELETE FROM annotations WHERE id = ?", (annotation_id,))
        self._connection.commit()

    @staticmethod
    def _to_entity(row: tuple) -> Annotation:
        return Annotation(
            id=row[0],
            book_id=row[1],
            page_number=row[2],
            content=row[3],
            created_at=datetime.fromisoformat(row[4]),
        )
