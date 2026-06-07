"""
Routes pour les projets SaaS / perso du Project Hub.

Pages HTML :
- GET /projects/           → tableau de bord de tous les projets
- GET /projects/{slug}    → détail d'un projet
- GET /projects/weekly    → planning hebdomadaire

API JSON :
- GET  /api/projects            → liste
- GET  /api/projects/{slug}     → détail
- POST /api/projects/{id}/log   → ajouter un log
- POST /api/projects/{id}/objective   → ajouter objectif
- POST /api/projects/{id}/objective/{oid}/toggle   → basculer objectif
- GET  /api/dashboard           → stats
- GET  /api/weekly-plan         → planning hebdo
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from sqlite3 import Connection
from datetime import date

from app.database import get_db
from app.services import project_service

router = APIRouter(tags=["projects"])


# ─── Pages HTML ────────────────────────────────────────

@router.get("/projects/")
def projects_dashboard(
    request: Request,
    db: Connection = Depends(get_db),
):
    """Tableau de bord : tous les projets + objectifs du jour."""
    projects = project_service.get_all_projects(db)
    today_objectives = project_service.get_all_today_objectives(db)
    stats = project_service.get_dashboard_stats(db)

    return request.app.state.templates.TemplateResponse(
        request,
        "projects/dashboard.html",
        {
            "request": request,
            "projects": projects,
            "today_objectives": today_objectives,
            "stats": stats,
            "today": date.today().isoformat(),
        },
    )


@router.get("/projects/weekly")
def weekly_plan(
    request: Request,
    db: Connection = Depends(get_db),
):
    """Planning hebdomadaire."""
    plan = project_service.get_weekly_plan(db)
    return request.app.state.templates.TemplateResponse(
        request,
        "projects/weekly.html",
        {
            "request": request,
            "plan": plan,
            "today_idx": __import__("datetime").datetime.now().weekday(),
            "today": date.today().isoformat(),
        },
    )


@router.get("/projects/{slug}")
def project_detail(
    slug: str,
    request: Request,
    db: Connection = Depends(get_db),
):
    """Page détail d'un projet avec historique + objectifs."""
    project = project_service.get_project_by_slug(db, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    logs = project_service.get_project_logs(db, project["id"])
    objectives = project_service.get_today_objectives(db, project["id"])

    return request.app.state.templates.TemplateResponse(
        request,
        "projects/detail.html",
        {
            "request": request,
            "project": project,
            "logs": logs,
            "objectives": objectives,
            "today": date.today().isoformat(),
        },
    )


# ─── API JSON ──────────────────────────────────────────

@router.get("/api/projects")
def api_list_projects(
    db: Connection = Depends(get_db),
):
    """Liste tous les projets."""
    return project_service.get_all_projects(db)


@router.get("/api/projects/{slug}")
def api_project_detail(
    slug: str,
    db: Connection = Depends(get_db),
):
    """Détail d'un projet."""
    project = project_service.get_project_by_slug(db, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    project["logs"] = project_service.get_project_logs(db, project["id"], limit=50)
    project["objectives"] = project_service.get_today_objectives(db, project["id"])
    return project


@router.post("/api/projects/{project_id}/log")
async def api_add_log(
    project_id: int,
    request: Request,
    db: Connection = Depends(get_db),
):
    """Ajoute un log dans l'historique d'un projet."""
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    body = await request.json()
    content = body.get("content", "")
    entry_type = body.get("entry_type", "session")

    if not content:
        raise HTTPException(status_code=400, detail="Le contenu est requis")

    project_service.add_project_log(db, project_id, content, entry_type)
    return {"ok": True}


@router.post("/api/projects/{project_id}/log/form")
def api_add_log_form(
    project_id: int,
    request: Request,
    content: str = Form(...),
    entry_type: str = Form("session"),
    db: Connection = Depends(get_db),
):
    """Ajoute un log via formulaire htmx."""
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    project_service.add_project_log(db, project_id, content, entry_type)
    return HTMLResponse(
        request.app.state.templates.TemplateResponse(
            request,
            "projects/_log_list.html",
            {
                "request": request,
                "logs": project_service.get_project_logs(db, project_id),
                "project": project,
            },
        ).body
    )


@router.post("/api/projects/{project_id}/objective")
def api_add_objective(
    project_id: int,
    request: Request,
    objective: str = Form(...),
    for_date: str = Form(""),
    db: Connection = Depends(get_db),
):
    """Ajoute un objectif via formulaire htmx."""
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    fd = for_date.strip() or None
    project_service.add_objective(db, project_id, objective, fd)
    return HTMLResponse(
        request.app.state.templates.TemplateResponse(
            request,
            "projects/_objective_list.html",
            {
                "request": request,
                "objectives": project_service.get_today_objectives(db, project_id),
                "project": project,
            },
        ).body
    )


@router.post("/api/projects/{project_id}/objective/{objective_id}/toggle")
def api_toggle_objective(
    project_id: int,
    objective_id: int,
    request: Request,
    db: Connection = Depends(get_db),
):
    """Bascule un objectif completed/incompleted."""
    project_service.toggle_objective(db, objective_id)
    return HTMLResponse(
        request.app.state.templates.TemplateResponse(
            request,
            "projects/_objective_list.html",
            {
                "request": request,
                "objectives": project_service.get_today_objectives(db, project_id),
                "project": project_service.get_project_by_id(db, project_id),
            },
        ).body
    )


@router.get("/api/dashboard")
def api_dashboard(
    db: Connection = Depends(get_db),
):
    """Statistiques pour le tableau de bord."""
    return project_service.get_dashboard_stats(db)


@router.get("/api/weekly-plan")
def api_weekly_plan(
    db: Connection = Depends(get_db),
):
    """Planning hebdomadaire."""
    return project_service.get_weekly_plan(db)
