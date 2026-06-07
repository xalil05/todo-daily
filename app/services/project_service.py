"""
Service pour la gestion des projets / SaaS.

Opérations CRUD sur les tables :
- projects
- project_logs (historique)
- project_objectives (objectifs du jour)
"""

import sqlite3
from datetime import date


# ─── Projets ────────────────────────────────────────────

def get_all_projects(db: sqlite3.Connection):
    """Retourne tous les projets, triés par sort_order."""
    rows = db.execute(
        "SELECT * FROM projects ORDER BY sort_order ASC, name ASC"
    ).fetchall()
    return [dict(r) for r in rows]


def get_projects_by_status(db: sqlite3.Connection, status=None):
    if status:
        rows = db.execute(
            "SELECT * FROM projects WHERE status = ? ORDER BY sort_order ASC", (status,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM projects ORDER BY sort_order ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_project_by_slug(db: sqlite3.Connection, slug: str):
    row = db.execute("SELECT * FROM projects WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None


def get_project_by_id(db: sqlite3.Connection, project_id: int):
    row = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return dict(row) if row else None


def create_project(db: sqlite3.Connection, name: str, slug: str, **kwargs):
    db.execute(
        """
        INSERT INTO projects (name, slug, short_name, description, category, status, color, icon, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            slug,
            kwargs.get("short_name"),
            kwargs.get("description"),
            kwargs.get("category", "saas"),
            kwargs.get("status", "active"),
            kwargs.get("color", "#6366f1"),
            kwargs.get("icon", "📁"),
            kwargs.get("sort_order", 0),
        ),
    )
    db.commit()
    return get_project_by_slug(db, slug)


def update_project_status(db: sqlite3.Connection, project_id: int, status: str):
    db.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))
    db.commit()


# ─── Projets par défaut (seed) ─────────────────────────

SEED_PROJECTS = [
    {
        "name": "Dossier Bankable",
        "slug": "dossier-bankable",
        "short_name": "🏦 Dossier Bankable",
        "description": "Automatisation de dossiers d'entreprise bankables — études marché, finance, juridique, risque.",
        "category": "saas",
        "status": "active",
        "color": "#6366f1",
        "icon": "🏦",
        "sort_order": 1,
    },
    {
        "name": "BugCrush",
        "slug": "bugcrush",
        "short_name": "🐛 BugCrush",
        "description": "Pipeline de débogage automatisé SaaS — Triage, reproduction, diagnostic, correction et validation sécurité.",
        "category": "saas",
        "status": "active",
        "color": "#ef4444",
        "icon": "🐛",
        "sort_order": 2,
    },
    {
        "name": "SecureShield",
        "slug": "secureshield",
        "short_name": "🛡️ SecureShield",
        "description": "Audit cybersécurité SaaS — OSINT, pentest, forensique, conformité RGPD/ISO et monitoring.",
        "category": "saas",
        "status": "active",
        "color": "#10b981",
        "icon": "🛡️",
        "sort_order": 3,
    },
    {
        "name": "Melo Studio",
        "slug": "melo-studio",
        "short_name": "🎨 Melo Studio",
        "description": "Direction artistique SaaS — branding, pitch decks, contenu social et génération d'images IA.",
        "category": "saas",
        "status": "active",
        "color": "#8b5cf6",
        "icon": "🎨",
        "sort_order": 4,
    },
    {
        "name": "ProjecSen",
        "slug": "projecsen",
        "short_name": "🌍 ProjecSen",
        "description": "Simulateur de projections démographiques et économiques multi-agents pour le Sénégal. Frontend Next.js + Backend Flask.",
        "category": "perso",
        "status": "active",
        "color": "#14b8a6",
        "icon": "🌍",
        "sort_order": 5,
    },
    {
        "name": "BELLISSIMA",
        "slug": "bellissima",
        "short_name": "🧺 BELLISSIMA",
        "description": "Projet Smart Laundry premium Dakar. Suivi fournisseurs (Electrolux, DIMINTER, Domotiq, Diotali), planning, devis.",
        "category": "perso",
        "status": "active",
        "color": "#3b82f6",
        "icon": "🧺",
        "sort_order": 6,
    },
    {
        "name": "Nexus-Debug",
        "slug": "nexus-debug",
        "short_name": "🔍 Nexus",
        "description": "Système agentique de débogage avec dashboard, notifications Telegram, webhooks. Hub multi-tenant.",
        "category": "perso",
        "status": "active",
        "color": "#64748b",
        "icon": "🔍",
        "sort_order": 7,
    },
    {
        "name": "Prompto",
        "slug": "prompto",
        "short_name": "⚡ Prompto",
        "description": "Prompt Factory — transforme un brief en prompt prêt à copier-coller.",
        "category": "saas",
        "status": "draft",
        "color": "#f59e0b",
        "icon": "⚡",
        "sort_order": 8,
    },
    {
        "name": "Python Learning",
        "slug": "python-learning",
        "short_name": "🐍 Python",
        "description": "Apprentissage Python — exercices, corrections, push sur GitHub xalil05/python-learning.",
        "category": "perso",
        "status": "active",
        "color": "#22c55e",
        "icon": "🐍",
        "sort_order": 9,
    },
    {
        "name": "Todo Daily",
        "slug": "todo-daily",
        "short_name": "✅ Todo",
        "description": "Application de gestion de tâches quotidienne (FastAPI + SQLite + htmx) qui devient notre Project Hub central.",
        "category": "perso",
        "status": "active",
        "color": "#6366f1",
        "icon": "✅",
        "sort_order": 10,
    },
]


def seed_projects(db: sqlite3.Connection):
    """Insère les projets par défaut s'ils n'existent pas encore."""
    existing = {r["slug"] for r in get_all_projects(db)}
    for p in SEED_PROJECTS:
        if p["slug"] not in existing:
            create_project(db, **p)


# ─── Logs (historique) ─────────────────────────────────

def get_project_logs(db: sqlite3.Connection, project_id: int, limit: int = 20):
    """Retourne les logs d'un projet, du plus récent au plus ancien."""
    rows = db.execute(
        "SELECT * FROM project_logs WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
        (project_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def add_project_log(db: sqlite3.Connection, project_id: int, content: str, entry_type: str = "session"):
    """Ajoute une entrée dans l'historique d'un projet."""
    db.execute(
        "INSERT INTO project_logs (project_id, content, entry_type) VALUES (?, ?, ?)",
        (project_id, content, entry_type),
    )
    db.commit()


# ─── Objectifs du jour ─────────────────────────────────

def get_today_objectives(db: sqlite3.Connection, project_id: int):
    """Retourne les objectifs du jour pour un projet."""
    today = date.today().isoformat()
    rows = db.execute(
        """SELECT * FROM project_objectives
           WHERE project_id = ? AND (for_date IS NULL OR for_date = ?)
           ORDER BY sort_order ASC""",
        (project_id, today),
    ).fetchall()
    return [dict(r) for r in rows]


def get_all_today_objectives(db: sqlite3.Connection):
    """Retourne tous les objectifs du jour pour le tableau de bord."""
    today = date.today().isoformat()
    rows = db.execute(
        """SELECT po.*, p.name, p.slug, p.icon, p.color
           FROM project_objectives po
           JOIN projects p ON p.id = po.project_id
           WHERE (po.for_date IS NULL OR po.for_date = ?)
           ORDER BY po.sort_order ASC""",
        (today,),
    ).fetchall()
    return [dict(r) for r in rows]


def add_objective(db: sqlite3.Connection, project_id: int, objective: str, for_date: str = None):
    """Ajoute un objectif pour un projet."""
    db.execute(
        "INSERT INTO project_objectives (project_id, objective, for_date) VALUES (?, ?, ?)",
        (project_id, objective, for_date),
    )
    db.commit()


def toggle_objective(db: sqlite3.Connection, objective_id: int):
    """Bascule l'état completed d'un objectif."""
    row = db.execute(
        "SELECT completed FROM project_objectives WHERE id = ?", (objective_id,)
    ).fetchone()
    if row:
        new_val = 0 if row["completed"] else 1
        db.execute(
            "UPDATE project_objectives SET completed = ? WHERE id = ?",
            (new_val, objective_id),
        )
        db.commit()
        return new_val
    return None


# ─── Dashboard ─────────────────────────────────────────

def get_dashboard_stats(db: sqlite3.Connection):
    """Statistiques pour le tableau de bord."""
    projects = get_all_projects(db)
    active_saas = sum(1 for p in projects if p["category"] == "saas" and p["status"] == "active")
    active_perso = sum(1 for p in projects if p["category"] == "perso" and p["status"] == "active")
    total_logs = db.execute("SELECT COUNT(*) as c FROM project_logs").fetchone()["c"]
    total_objectives = db.execute(
        "SELECT COUNT(*) as c FROM project_objectives WHERE completed = 0"
    ).fetchone()["c"]
    return {
        "total_projects": len(projects),
        "active_saas": active_saas,
        "active_perso": active_perso,
        "total_logs": total_logs,
        "pending_objectives": total_objectives,
        "today_focus": get_today_focus(),
    }


# ─── Planification hebdomadaire ────────────────────────

WEEKLY_PLAN = [
    # (day_name, primary_project_slug, secondary_project_slug)
    ("Lundi", "dossier-bankable", "bellissima"),
    ("Mardi", "bugcrush", "todo-daily"),
    ("Mercredi", "secureshield", "projecsen"),
    ("Jeudi", "melo-studio", "python-learning"),
    ("Vendredi", None, None),       # Opérations / bouclage
    ("Samedi", None, None),         # R&D / libre
    ("Dimanche", None, None),       # Repos
]

WEEKDAYS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def get_today_focus():
    """Retourne le focus du jour (day_name, primary_slug, secondary_slug)."""
    from datetime import datetime
    today_idx = datetime.now().weekday()  # 0=Lundi
    if today_idx < len(WEEKLY_PLAN):
        return WEEKLY_PLAN[today_idx]
    return (None, None, None)


def get_weekly_plan(db: sqlite3.Connection):
    """Retourne le planning hebdomadaire avec les infos projets."""
    result = []
    for day_name, primary_slug, secondary_slug in WEEKLY_PLAN:
        entry = {
            "day": day_name,
            "primary": None,
            "secondary": None,
        }
        if primary_slug:
            p = get_project_by_slug(db, primary_slug)
            if p:
                entry["primary"] = p
        if secondary_slug:
            s = get_project_by_slug(db, secondary_slug)
            if s:
                entry["secondary"] = s
        result.append(entry)
    return result
