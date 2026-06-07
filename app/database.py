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
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
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
        # ── Table todos (existante) ──
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT NULL,
                due_date TEXT DEFAULT NULL,
                due_time TEXT DEFAULT NULL,
                priority TEXT NOT NULL DEFAULT 'moyenne'
                    CHECK (priority IN ('haute', 'moyenne', 'basse')),
                completed INTEGER NOT NULL DEFAULT 0
                    CHECK (completed IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        # Migration : ajouter due_time si la colonne n'existe pas encore
        try:
            conn.execute("ALTER TABLE todos ADD COLUMN due_time TEXT DEFAULT NULL")
        except Exception:
            pass  # Colonne due_time existe déjà

        # ── Table categories (existante) ──
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

        # ── Table projects (nouvelle) ──
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE,
                short_name TEXT DEFAULT NULL,
                description TEXT DEFAULT NULL,
                category TEXT DEFAULT 'saas'
                    CHECK (category IN ('saas', 'perso', 'client')),
                status TEXT DEFAULT 'active'
                    CHECK (status IN ('active', 'paused', 'completed', 'draft')),
                color TEXT DEFAULT '#6366f1',
                icon TEXT DEFAULT '📁',
                sort_order INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )

        # ── Table project_logs (nouvelle) ──
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                entry_type TEXT DEFAULT 'session'
                    CHECK (entry_type IN ('session', 'note', 'milestone', 'decision')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )

        # ── Table project_objectives (nouvelle) ──
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                objective TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
                    CHECK (completed IN (0, 1)),
                for_date TEXT DEFAULT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )

        conn.commit()
    finally:
        conn.close()
