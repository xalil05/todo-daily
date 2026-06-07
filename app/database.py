"""
Module de connexion à la base de données SQLite.

Utilise le module sqlite3 de la bibliothèque standard.
Crée automatiquement les tables.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "todo-daily.db"


def get_db() -> sqlite3.Connection:
    """
    Ouvre une connexion à la base SQLite et la retourne.
    Configure row_factory pour accéder aux colonnes par nom.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Crée les tables si elles n'existent pas encore.
    Appelée au démarrage de l'application.
    """
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT NULL,
                due_date TEXT DEFAULT NULL,
                priority TEXT NOT NULL DEFAULT 'moyenne'
                    CHECK (priority IN ('haute', 'moyenne', 'basse')),
                completed INTEGER NOT NULL DEFAULT 0
                    CHECK (completed IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT '#6366f1',
                sort_order INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
