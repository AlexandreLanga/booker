from __future__ import annotations

import sqlite3
from datetime import datetime

from domain.entities import Book


class SqliteBookRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def add(self, book: Book) -> Book:
        cursor = self._connection.execute(
            "INSERT INTO books (title, file_path, total_pages, added_at) VALUES (?, ?, ?, ?)",
            (book.title, book.file_path, book.total_pages, book.added_at.isoformat()),
        )
        self._connection.commit()
        book.id = cursor.lastrowid
        return book

    def get_by_id(self, book_id: int) -> Book | None:
        row = self._connection.execute(
            "SELECT id, title, file_path, total_pages, added_at FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()
        return self._to_entity(row) if row else None

    def get_by_path(self, file_path: str) -> Book | None:
        row = self._connection.execute(
            "SELECT id, title, file_path, total_pages, added_at FROM books WHERE file_path = ?",
            (file_path,),
        ).fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[Book]:
        rows = self._connection.execute(
            "SELECT id, title, file_path, total_pages, added_at FROM books ORDER BY added_at DESC"
        ).fetchall()
        return [self._to_entity(row) for row in rows]

    def delete(self, book_id: int) -> None:
        self._connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self._connection.commit()

    @staticmethod
    def _to_entity(row: tuple) -> Book:
        return Book(
            id=row[0],
            title=row[1],
            file_path=row[2],
            total_pages=row[3],
            added_at=datetime.fromisoformat(row[4]),
        )
