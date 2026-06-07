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

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from sqlite3 import Connection

from app.database import get_db
from app.models import Todo, TodoCreate, TodoUpdate
from app.services import todo_service
from app.routers.pages import _render_todo_partial

router = APIRouter(
    prefix="/api/todos",
    tags=["todos"],
)


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
            _render_todo_partial(request, "all", db).body
        )

    return updated


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
            _render_todo_partial(request, "all", db).body
        )
    # Pas de return → FastAPI renverra automatiquement une réponse 204 vide
