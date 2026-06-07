"""
Routes pour les pages HTML (rendu côté serveur avec Jinja2).

- GET / : page d'accueil avec la liste des tâches et les compteurs.
- POST /todos : création via formulaire htmx (renvoie HTML au lieu de JSON)
"""

from fastapi import APIRouter, Request, Depends, Query, Form
from sqlite3 import Connection

from app.database import get_db
from app.services import todo_service
from app.models import TodoCreate


def _render_todo_partial(request: Request, filter: str, db: Connection):
    """Rendu du partial _todo_list.html avec les données actuelles."""
    if filter not in ("all", "active", "done"):
        filter = "all"
    todos = todo_service.get_todos(db, filter_status=filter if filter != "all" else None)
    counts = todo_service.count_todos(db)
    return request.app.state.templates.TemplateResponse(
        request,
        "_todo_list.html",
        {
            "request": request,
            "todos": todos,
            "counts": counts,
            "filter": filter,
        },
    )


router = APIRouter(
    tags=["pages"],
)


@router.get("/")
def home(
    request: Request,
    filter: str = Query("all", alias="filter"),
    db: Connection = Depends(get_db),
):
    """
    Page d'accueil de l'application.

    Si la requête vient de htmx (en-tête HX-Request présent),
    on renvoie uniquement le partial _todo_list.html pour mise à jour
    du conteneur #main-content sans rechargement de page.
    Sinon, on renvoie la page complète index.html.
    """
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        return _render_todo_partial(request, filter, db)

    # Requête normale : page complète
    if filter not in ("all", "active", "done"):
        filter = "all"
    todos = todo_service.get_todos(db, filter_status=filter if filter != "all" else None)
    counts = todo_service.count_todos(db)

    return request.app.state.templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "todos": todos,
            "counts": counts,
            "filter": filter,
        },
    )


@router.post("/todos")
def create_todo_htmx(
    request: Request,
    title: str = Form(...),
    priority: str = Form("moyenne"),
    db: Connection = Depends(get_db),
):
    """
    Crée une tâche via le formulaire htmx.

    Reçoit les données du formulaire (title, priority),
    crée la tâche en base, et renvoie le partial _todo_list.html
    mis à jour pour remplacer #main-content.
    """
    if not title.strip():
        return _render_todo_partial(request, "all", db)

    data = TodoCreate(title=title.strip(), priority=priority)
    todo_service.create_todo(db, data)
    return _render_todo_partial(request, "all", db)
