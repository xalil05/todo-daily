"""
Service métier pour les opérations CRUD sur les tâches.

Toutes les fonctions reçoivent une connexion SQLite en paramètre
(principe d'injection de dépendances). Elles ne dépendent pas de FastAPI.
"""

import sqlite3
from typing import Optional

from app.models import Todo, TodoCreate, TodoUpdate


def create_todo(db: sqlite3.Connection, data: TodoCreate) -> Todo:
    """
    Insère une nouvelle tâche en base et retourne l'objet Todo créé.

    Args:
        db: Connexion SQLite active
        data: Données validées (title, priority)

    Returns:
        Le modèle Todo avec son id, sa date de création et completed=False
    """
    cursor = db.execute(
        "INSERT INTO todos (title, priority) VALUES (?, ?)",
        (data.title, data.priority),
    )
    db.commit()

    # On récupère la ligne fraîchement insérée grâce à l'id auto-généré
    new_id = cursor.lastrowid
    row = db.execute("SELECT * FROM todos WHERE id = ?", (new_id,)).fetchone()
    return Todo.model_validate(dict(row))


def get_todos(
    db: sqlite3.Connection,
    filter_status: Optional[str] = None,
) -> list[Todo]:
    """
    Récupère la liste des tâches, avec un filtre optionnel.

    Args:
        db: Connexion SQLite active
        filter_status: 'done' pour les tâches terminées,
                       'active' pour les tâches en cours,
                       None ou 'all' pour tout récupérer

    Returns:
        Liste de modèles Todo, triés par date de création (plus récentes d'abord)
    """
    query = "SELECT * FROM todos"
    params = ()

    if filter_status == "done":
        query += " WHERE completed = 1"
    elif filter_status == "active":
        query += " WHERE completed = 0"
    # Si None ou 'all', pas de filtre

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
    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
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
