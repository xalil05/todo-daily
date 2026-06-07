"""
Service métier pour les opérations CRUD sur les tâches.

Toutes les fonctions reçoivent une connexion SQLite en paramètre
(principe d'injection de dépendances). Elles ne dépendent pas de FastAPI.
"""

import sqlite3
from typing import Optional

from app.models import Todo, TodoCreate, TodoUpdate

# Colonnes explicites pour éviter les SELECT *
TODOS_COLUMNS = "id, title, category, due_date, due_time, priority, completed, created_at"
CATEGORIES_COLUMNS = "id, name, color, sort_order"


def create_todo(db: sqlite3.Connection, data: TodoCreate) -> Todo:
    """
    Insère une nouvelle tâche en base et retourne l'objet Todo créé.
    """
    cursor = db.execute(
        "INSERT INTO todos (title, category, due_date, due_time, priority) VALUES (?, ?, ?, ?, ?)",
        (data.title, data.category, data.due_date, data.due_time, data.priority),
    )
    db.commit()

    # On récupère la ligne fraîchement insérée grâce à l'id auto-généré
    new_id = cursor.lastrowid
    row = db.execute(f"SELECT {TODOS_COLUMNS} FROM todos WHERE id = ?", (new_id,)).fetchone()
    return Todo.model_validate(dict(row))


def get_todos(
    db: sqlite3.Connection,
    filter_status: Optional[str] = None,
    filter_category: Optional[str] = None,
) -> list[Todo]:
    """
    Récupère la liste des tâches, avec filtres optionnels.
    """
    conditions = []
    params = ()

    if filter_status == "done":
        conditions.append("completed = 1")
    elif filter_status == "active":
        conditions.append("completed = 0")

    if filter_category:
        conditions.append("category = ?")
        params = params + (filter_category,)

    query = "SELECT " + TODOS_COLUMNS + " FROM todos"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"
    rows = db.execute(query, params).fetchall()
    return [Todo.model_validate(dict(row)) for row in rows]


def get_todo_by_id(db: sqlite3.Connection, todo_id: int) -> Optional[Todo]:
    """
    Récupère une tâche par son identifiant.

    Args:
        db: Connexion SQLite active
        todo_id: Identifiant de la tâche

    Returns:
        Le Todo correspondant ou None si l'id n'existe pas
    """
    row = db.execute(f"SELECT {TODOS_COLUMNS} FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        return None
    return Todo.model_validate(dict(row))


def update_todo_completed(
    db: sqlite3.Connection, todo_id: int, data: TodoUpdate
) -> Optional[Todo]:
    """
    Marque une tâche comme terminée ou non.

    Args:
        db: Connexion SQLite active
        todo_id: Identifiant de la tâche à modifier
        data: Contient completed = True/False

    Returns:
        Le Todo mis à jour, ou None si l'id n'existe pas
    """
    # Vérification que la tâche existe
    existing = get_todo_by_id(db, todo_id)
    if existing is None:
        return None

    # Conversion du booléen en entier pour SQLite
    completed_int = 1 if data.completed else 0
    db.execute(
        "UPDATE todos SET completed = ? WHERE id = ?",
        (completed_int, todo_id),
    )
    db.commit()
    return get_todo_by_id(db, todo_id)


def delete_todo(db: sqlite3.Connection, todo_id: int) -> bool:
    """
    Supprime une tâche par son identifiant.

    Args:
        db: Connexion SQLite active
        todo_id: Identifiant de la tâche à supprimer

    Returns:
        True si une tâche a été supprimée, False si l'id n'existait pas
    """
    cursor = db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    db.commit()
    return cursor.rowcount > 0


def update_todo_title(
    db: sqlite3.Connection, todo_id: int, new_title: str
) -> Optional[Todo]:
    """
    Modifie le titre d'une tâche.

    Args:
        db: Connexion SQLite active
        todo_id: Identifiant de la tâche à modifier
        new_title: Nouveau titre

    Returns:
        Le Todo mis à jour, ou None si l'id n'existe pas
    """
    existing = get_todo_by_id(db, todo_id)
    if existing is None:
        return None

    db.execute(
        "UPDATE todos SET title = ? WHERE id = ?",
        (new_title.strip(), todo_id),
    )
    db.commit()
    return get_todo_by_id(db, todo_id)


def count_todos(db: sqlite3.Connection) -> dict[str, int]:
    """
    Retourne le nombre total de tâches, le nombre de tâches actives et terminées.
    Utile pour l'affichage des compteurs dans l'interface.

    Args:
        db: Connexion SQLite active

    Returns:
        Dictionnaire avec les clés 'total', 'active', 'done'
    """
    total = db.execute("SELECT COUNT(*) FROM todos").fetchone()[0]
    done = db.execute("SELECT COUNT(*) FROM todos WHERE completed = 1").fetchone()[0]
    active = total - done
    return {"total": total, "active": active, "done": done}


def get_next_due(db: sqlite3.Connection) -> Optional[dict]:
    """
    Retourne la prochaine tâche non terminée avec date/heure d'échéance.
    Utilisé par le timer intégré dans l'app.
    """
    from datetime import datetime

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    rows = db.execute(
        f"SELECT {TODOS_COLUMNS} FROM todos WHERE completed = 0 AND due_date IS NOT NULL ORDER BY due_date ASC, due_time ASC"
    ).fetchall()

    for row in rows:
        todo = dict(row)
        if todo["due_date"] < today:
            continue  # Déjà passée
        if todo["due_date"] == today and todo["due_time"] and todo["due_time"] < current_time:
            continue  # Heure déjà passée
        return {
            "id": todo["id"],
            "title": todo["title"],
            "due_date": todo["due_date"],
            "due_time": todo["due_time"],
            "priority": todo["priority"],
        }
    return None


# ─── Catégories ────────────────────────────────────────────────


def get_categories(db: sqlite3.Connection) -> list[dict]:
    """Liste toutes les catégories triées par ordre."""
    rows = db.execute(
        f"SELECT {CATEGORIES_COLUMNS} FROM categories ORDER BY sort_order ASC, name ASC"
    ).fetchall()
    return [dict(r) for r in rows]


def create_category(db: sqlite3.Connection, name: str, color: str = "#6366f1") -> dict:
    """Crée une catégorie et la retourne."""
    cursor = db.execute(
        "INSERT INTO categories (name, color) VALUES (?, ?)",
        (name.strip(), color),
    )
    db.commit()
    row = db.execute(f"SELECT {CATEGORIES_COLUMNS} FROM categories WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


def delete_category(db: sqlite3.Connection, category_id: int) -> bool:
    """Supprime une catégorie. Les tâches gardent leur catégorie (texte)."""
    cursor = db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    db.commit()
    return cursor.rowcount > 0


def get_category_names(db: sqlite3.Connection) -> list[str]:
    """Retourne la liste des noms de catégories existantes."""
    rows = db.execute("SELECT name FROM categories ORDER BY sort_order, name").fetchall()
    return [r["name"] for r in rows]
