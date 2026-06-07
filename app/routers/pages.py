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


def _render_todo_partial(
    request: Request, filter: str, category: str | None, db: Connection
):
    """Rendu du partial _todo_list.html avec les données actuelles."""
    if filter not in ("all", "active", "done"):
        filter = "all"
    cat = category if category and category != "all" else None

    todos = todo_service.get_todos(db, filter_status=filter if filter != "all" else None, filter_category=cat)
    counts = todo_service.count_todos(db)
    categories = todo_service.get_categories(db)

    return request.app.state.templates.TemplateResponse(
        request,
        "_todo_list.html",
        {
            "request": request,
            "todos": todos,
            "counts": counts,
            "categories": categories,
            "filter": filter,
            "current_category": category or "all",
        },
    )


router = APIRouter(
    tags=["pages"],
)


@router.get("/")
def home(
    request: Request,
    filter: str = Query("all", alias="filter"),
    category: str = Query("all", alias="category"),
    db: Connection = Depends(get_db),
):
    """
    Page d'accueil de l'application.
    """
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        return _render_todo_partial(request, filter, category, db)

    # Requête normale : page complète
    if filter not in ("all", "active", "done"):
        filter = "all"
    cat = category if category and category != "all" else None

    todos = todo_service.get_todos(db, filter_status=filter if filter != "all" else None, filter_category=cat)
    counts = todo_service.count_todos(db)
    categories = todo_service.get_categories(db)

    return request.app.state.templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "todos": todos,
            "counts": counts,
            "categories": categories,
            "filter": filter,
            "current_category": category,
        },
    )


@router.post("/todos")
def create_todo_htmx(
    request: Request,
    title: str = Form(...),
    priority: str = Form("moyenne"),
    category: str = Form(""),
    db: Connection = Depends(get_db),
):
    """
    Crée une tâche via le formulaire htmx.
    """
    if not title.strip():
        return _render_todo_partial(request, "all", None, db)

    cat = category.strip() or None
    data = TodoCreate(title=title.strip(), priority=priority, category=cat)
    todo_service.create_todo(db, data)
    return _render_todo_partial(request, "all", None, db)
