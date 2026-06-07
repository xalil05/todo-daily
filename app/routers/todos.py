"""
Routes de l'API Todo (JSON).

Fournit les endpoints CRUD classiques :
- POST   /api/todos        → créer une tâche
- GET    /api/todos        → lister (avec filtre optionnel)
- GET    /api/todos/{id}   → détail d'une tâche
- PATCH  /api/todos/{id}   → marquer terminée / non terminée
- DELETE /api/todos/{id}   → supprimer
- GET    /api/todos/counts → compteurs (total, actives, terminées)

Les routes PATCH et DELETE détectent les requêtes htmx (HX-Request)
pour renvoyer le partial HTML au lieu du JSON, permettant une mise à jour
du #main-content sans rechargement.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from sqlite3 import Connection
import html

from app.database import get_db
from app.models import Todo, TodoCreate, TodoUpdate, TodoUpdateTitle
from app.services import todo_service
from app.routers.pages import _render_todo_partial

router = APIRouter(
    prefix="/api/todos",
    tags=["todos"],
)


@router.get("/{todo_id}/edit")
def edit_todo_form(
    todo_id: int,
    request: Request,
    db: Connection = Depends(get_db),
):
    """
    Renvoie un formulaire HTML inline pour éditer le titre d'une tâche.
    Utilisé par htmx (double-click sur le titre).
    """
    todo = todo_service.get_todo_by_id(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Tâche introuvable")

    return HTMLResponse(f"""\
    <form class="inline-flex items-center gap-1 w-full"
          hx-put="/api/todos/{todo.id}/title"
          hx-target="#main-content"
          hx-trigger="submit">
        <input type="text" name="title" value="{html.escape(todo.title)}"
               maxlength="200" required autofocus
               onfocus="this.select()"
               class="flex-1 min-w-0 rounded-lg border border-indigo-400 dark:border-indigo-500 bg-white dark:bg-gray-700 px-3 py-1.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30">
        <button type="submit"
                class="shrink-0 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-indigo-700 active:bg-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 transition-colors">
            OK
        </button>
    </form>
    """)

# ─── Catégories ────────────────────────────────────────

@router.get("/categories", response_model=list[dict])
def list_categories(db: Connection = Depends(get_db)):
    """Liste toutes les catégories."""
    return todo_service.get_categories(db)


@router.post("/categories", response_model=dict, status_code=201)
def add_category(
    data: dict,
    db: Connection = Depends(get_db),
):
    """Crée une nouvelle catégorie."""
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Le nom est requis")
    color = data.get("color", "#6366f1")
    try:
        return todo_service.create_category(db, name, color)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Catégorie déjà existante : {e}")


@router.delete("/categories/{category_id}", status_code=204)
def remove_category(
    category_id: int,
    request: Request,
    db: Connection = Depends(get_db),
):
    """Supprime une catégorie."""
    deleted = todo_service.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")


@router.post("/", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, db: Connection = Depends(get_db)):
    """
    Crée une nouvelle tâche à partir des données validées (title, priority).
    Renvoie la tâche créée avec son id, sa date et son statut.
    """
    return todo_service.create_todo(db, data)


@router.get("/", response_model=list[Todo])
def list_todos(
    filter: str = "all",
    db: Connection = Depends(get_db),
):
    """
    Liste les tâches avec un filtre optionnel.
    - filter=all    : toutes les tâches
    - filter=active : seulement les tâches non terminées
    - filter=done   : seulement les tâches terminées
    """
    if filter not in ("all", "active", "done"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Le filtre doit être 'all', 'active' ou 'done'",
        )
    return todo_service.get_todos(db, filter_status=filter if filter != "all" else None)


@router.get("/counts")
def get_counts(db: Connection = Depends(get_db)):
    """
    Retourne un dictionnaire avec le nombre total de tâches,
    le nombre de tâches actives et le nombre de tâches terminées.
    """
    return todo_service.count_todos(db)


@router.get("/{todo_id}", response_model=Todo)
def get_todo(todo_id: int, db: Connection = Depends(get_db)):
    """
    Récupère une tâche par son identifiant.
    Retourne une erreur 404 si l'id n'existe pas.
    """
    todo = todo_service.get_todo_by_id(db, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune tâche trouvée avec l'id {todo_id}",
        )
    return todo


@router.post("/{todo_id}/toggle")
def toggle_todo(
    todo_id: int,
    request: Request,
    db: Connection = Depends(get_db),
):
    """Bascule l'état completed d'une tâche."""
    todo = todo_service.get_todo_by_id(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404)

    data = TodoUpdate(completed=not todo.completed)
    updated = todo_service.update_todo_completed(db, todo_id, data)
    
    if request.headers.get("HX-Request") == "true":
        return HTMLResponse(
            _render_todo_partial(request, "all", None, db).body
        )
    
    return updated


@router.patch("/{todo_id}", response_model=Todo)
def update_todo_completed(
    todo_id: int,
    data: TodoUpdate,
    request: Request,
    db: Connection = Depends(get_db),
):
    """
    Modifie l'état 'completed' d'une tâche.
    Si la requête vient de htmx, renvoie le partial HTML pour mise à jour
    du conteneur #main-content.
    Sinon, renvoie le Todo en JSON.
    """
    updated = todo_service.update_todo_completed(db, todo_id, data)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune tâche trouvée avec l'id {todo_id}",
        )

    # Si htmx : renvoyer le partial HTML au lieu du JSON
    if request.headers.get("HX-Request") == "true":
        return HTMLResponse(
            _render_todo_partial(request, "all", None, db).body
        )

    return updated


@router.put("/{todo_id}/title", response_model=Todo)
def update_todo_title(
    todo_id: int,
    request: Request,
    title: str = Form(...),
    db: Connection = Depends(get_db),
):
    """
    Modifie le titre d'une tâche.
    Si la requête vient de htmx, renvoie le partial HTML.
    """
    updated = todo_service.update_todo_title(db, todo_id, title)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune tâche trouvée avec l'id {todo_id}",
        )

    if request.headers.get("HX-Request") == "true":
        return HTMLResponse(
            _render_todo_partial(request, "all", None, db).body
        )

    return updated


@router.get("/next-due")
def get_next_due(request: Request, db: Connection = Depends(get_db)):
    """Prochaine tâche échue — utilisé par le timer intégré."""
    from datetime import datetime, timedelta
    next_task = todo_service.get_next_due(db)
    if next_task is None:
        return {"next": None}

    now = datetime.now()
    try:
        due = datetime.strptime(f"{next_task['due_date']} {next_task['due_time'] or '23:59'}", "%Y-%m-%d %H:%M")
    except ValueError:
        return {"next": None}

    remaining = (due - now).total_seconds()
    return {
        "next": {
            "id": next_task["id"],
            "title": next_task["title"],
            "due_date": next_task["due_date"],
            "due_time": next_task["due_time"],
            "remaining_seconds": max(0, int(remaining)),
            "overdue": remaining < 0,
        }
    }


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    request: Request,
    db: Connection = Depends(get_db),
):
    """
    Supprime une tâche.
    Si la requête vient de htmx, renvoie le partial HTML pour mise à jour
    du conteneur #main-content.
    Sinon, renvoie 204 (pas de contenu).
    """
    deleted = todo_service.delete_todo(db, todo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune tâche trouvée avec l'id {todo_id}",
        )

    # Si htmx : renvoyer le partial HTML au lieu du 204
    if request.headers.get("HX-Request") == "true":
        return HTMLResponse(
            _render_todo_partial(request, "all", None, db).body
        )
    # Pas de return → FastAPI renverra automatiquement une réponse 204 vide
