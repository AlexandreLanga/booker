from __future__ import annotations

import sqlite3
import json
from datetime import datetime

from domain.entities import Book


class SqliteBookRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def add(self, book: Book) -> Book:
        cursor = self._connection.execute(
            "INSERT INTO books (title, file_path, total_pages, added_at, author, publisher, isbn, "
            "publication_year, category, tags, favorite, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            self._values(book),
        )
        self._connection.commit()
        book.id = cursor.lastrowid
        return book

    def get_by_id(self, book_id: int) -> Book | None:
        row = self._connection.execute(
            self._select_columns() + " FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()
        return self._to_entity(row) if row else None

    def get_by_path(self, file_path: str) -> Book | None:
        row = self._connection.execute(
            self._select_columns() + " FROM books WHERE file_path = ?",
            (file_path,),
        ).fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[Book]:
        rows = self._connection.execute(
            self._select_columns() + " FROM books ORDER BY added_at DESC"
        ).fetchall()
        return [self._to_entity(row) for row in rows]

    def delete(self, book_id: int) -> None:
        self._connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self._connection.commit()

    def update(self, book: Book) -> Book:
        self._connection.execute(
            "UPDATE books SET title = ?, author = ?, publisher = ?, isbn = ?, publication_year = ?, "
            "category = ?, tags = ?, favorite = ?, status = ? WHERE id = ?",
            (
                book.title,
                book.author,
                book.publisher,
                book.isbn,
                book.publication_year,
                book.category,
                json.dumps(book.tags, ensure_ascii=False),
                int(book.favorite),
                book.status,
                book.id,
            ),
        )
        self._connection.commit()
        return book

    @staticmethod
    def _select_columns() -> str:
        return (
            "SELECT id, title, file_path, total_pages, added_at, author, publisher, isbn, "
            "publication_year, category, tags, favorite, status"
        )

    @staticmethod
    def _values(book: Book) -> tuple:
        return (
            book.title,
            book.file_path,
            book.total_pages,
            book.added_at.isoformat(),
            book.author,
            book.publisher,
            book.isbn,
            book.publication_year,
            book.category,
            json.dumps(book.tags, ensure_ascii=False),
            int(book.favorite),
            book.status,
        )

    @staticmethod
    def _to_entity(row: tuple) -> Book:
        return Book(
            id=row[0],
            title=row[1],
            file_path=row[2],
            total_pages=row[3],
            added_at=datetime.fromisoformat(row[4]),
            author=row[5] or "",
            publisher=row[6] or "",
            isbn=row[7] or "",
            publication_year=row[8],
            category=row[9] or "",
            tags=json.loads(row[10] or "[]"),
            favorite=bool(row[11]),
            status=row[12] or "Não iniciado",
        )
