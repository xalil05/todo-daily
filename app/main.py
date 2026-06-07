"""
Point d'entrée de l'application FastAPI Todo-Daily.

- Configure l'application avec un titre et une description.
- Initialise la base de données au démarrage.
- Inclut le router de l'API REST (todos) et, plus tard, celui des pages HTML.
- Monte le dossier statique pour le CSS personnalisé.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.services import project_service
from app.routers import todos, pages, projects


# Création de l'application FastAPI avec les métadonnées de base
app = FastAPI(
    title="Todo-Daily",
    description="Une todo list quotidienne simple, rapide et interactive.",
    version="0.1.0",
)


# --- Configuration Jinja2 ---
# On stocke l'instance Jinja2Templates dans app.state pour y accéder
# depuis les routes (pages.py utilise request.app.state.templates)
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)
app.state.templates = Jinja2Templates(directory=str(templates_dir))


# --- Événement déclenché au démarrage du serveur ---
@app.on_event("startup")
def on_startup():
    """
    Appelé une fois quand le serveur Uvicorn démarre.
    Crée la table 'todos' dans SQLite si elle n'existe pas encore.
    """
    init_db()
    conn = __import__("app.database", fromlist=["get_db"]).get_db()
    try:
        project_service.seed_projects(conn)
    finally:
        conn.close()
    print("✅ Base de données initialisée avec succès.")


# --- Inclusion des routers ---
# Router API JSON (toutes les routes commencent par /api/todos)
app.include_router(todos.router)

# Router des pages HTML (route /)
app.include_router(pages.router)

# Router des projets (pages + API)
app.include_router(projects.router)


# --- Dossier des fichiers statiques ---
# On monte le dossier app/static/ afin que le navigateur puisse accéder
# aux fichiers qu'il contient via l'URL /static/...
# Exemple : /static/css/style.css correspondra au fichier app/static/css/style.css
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)  # Crée le dossier si besoin
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
