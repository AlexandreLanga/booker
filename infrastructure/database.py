from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    total_pages INTEGER NOT NULL,
    added_at TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT '',
    publisher TEXT NOT NULL DEFAULT '',
    isbn TEXT NOT NULL DEFAULT '',
    publication_year INTEGER,
    category TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    favorite INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Não iniciado'
);

CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reading_progress (
    book_id INTEGER PRIMARY KEY,
    current_page INTEGER NOT NULL,
    last_read_at TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS page_markers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    points TEXT NOT NULL,
    color TEXT NOT NULL,
    alpha REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
);
"""


def create_connection(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(books)")}
    migrations = {
        "author": "ALTER TABLE books ADD COLUMN author TEXT NOT NULL DEFAULT ''",
        "publisher": "ALTER TABLE books ADD COLUMN publisher TEXT NOT NULL DEFAULT ''",
        "isbn": "ALTER TABLE books ADD COLUMN isbn TEXT NOT NULL DEFAULT ''",
        "publication_year": "ALTER TABLE books ADD COLUMN publication_year INTEGER",
        "category": "ALTER TABLE books ADD COLUMN category TEXT NOT NULL DEFAULT ''",
        "tags": "ALTER TABLE books ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'",
        "favorite": "ALTER TABLE books ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0",
        "status": "ALTER TABLE books ADD COLUMN status TEXT NOT NULL DEFAULT 'Não iniciado'",
    }
    for column, statement in migrations.items():
        if column not in columns:
            connection.execute(statement)
    connection.commit()
    return connection
