# Todo-Daily

**Hub central de gestion de projets SaaS et personnels.** Dashboard, planning hebdomadaire, suivi d'historique et objectifs du jour — le tout dans une app FastAPI légère avec htmx.

```text
10 projets · 4 SaaS · Planning intégré · Historique de sessions · 🐍 Python 15h-17h30
```

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🏠 **Dashboard projets** | Vue d'ensemble des 10 projets (SaaS + perso) avec statuts |
| 📅 **Planning hebdomadaire** | Focus principal/secondaire par jour (Lun→Sam) |
| 📄 **Page détail** | Historique + objectifs du jour par projet |
| 🎯 **Objectifs du jour** | Ajout, complétion, seed automatique pour le lendemain |
| 📜 **Historique de sessions** | Logging de fin de session avec `end-session` |
| 🎬 **Bouton Fin de session** | Modal sur chaque projet pour logger + objectiver demain |
| 🌙 **Dark mode** | Basculable, sauvegardé dans localStorage |
| 📱 **Responsive** | Tailwind CSS, mobile-first |

## 🚀 Stack

- Python 3.11+ / FastAPI
- SQLite (zero config)
- Jinja2 + htmx (AJAX sans JS)
- Tailwind CSS v4 (CDN)
- UV (package manager)
- Pillow (génération d'images)

## 🗓️ Planning hebdomadaire

| Jour | Focus principal | Secondaire |
|:---:|---|---|
| Lundi | 🏦 **Dossier Bankable** | 🧺 BELLISSIMA |
| Mardi | 🐛 **BugCrush** | ✅ Todo Daily |
| Mercredi | 🛡️ **SecureShield** | 🌍 ProjecSen |
| Jeudi | 🎨 **Melo Studio** | 🐍 Python Learning |
| Vendredi | 🧺 **BELLISSIMA** (fournisseurs) | 🔍 Nexus-Debug (maintenance) |
| Samedi | ⚡ **Prompto** (R&D) | 🐍 Python |
| Dimanche | ✅ **Todo-Daily** (planification) | — |

> 🐍 **Cours Python** : Lundi→Vendredi, 15h00-17h30 (todo automatique)

## 🏗️ SaaS en construction

- 🏦 **Dossier Bankable** — Automatisation dossiers d'entreprise bankables
- 🐛 **BugCrush** — Pipeline de débogage SaaS
- 🛡️ **SecureShield** — Audit cybersécurité
- 🎨 **Melo Studio** — Direction artistique
- ⚡ **Prompto** — Prompt Factory

## 🛠️ Utilisation

### Installation rapide

```bash
git clone https://github.com/xalil05/todo-daily.git
cd todo-daily
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Ouvrir http://localhost:8002 → Todos quotidiens
Ouvrir http://localhost:8002/projects → Hub projets

### Endpoints principaux

| URL | Description |
|:---|:---|
| `/` | Todos du jour |
| `/projects/` | Dashboard projets |
| `/projects/weekly` | Planning hebdomadaire |
| `/projects/{slug}` | Détail d'un projet |
| `/api/todos/` | API JSON des todos |
| `/api/projects` | API JSON des projets |
| `/api/dashboard` | Statistiques |
| `/api/weekly-plan` | Planning JSON |

### Navigation

- **✅ Todo** → Listes + filtres (all/active/done)
- **🏢 Projets** → Hub des 10 projets
- **📅 Semaine** → Planning hebdomadaire
- **🕒 Timer** → Affiché en haut : prochaine tâche due
- **🌙 Dark mode** → Bouton en haut à droite

### Rituel de fin de session

```bash
~/.hermes/scripts/end-session <projet> "Ce qu'on a fait" "Objectif de demain"
```

Ou depuis l'interface : bouton 🎬 Fin de session sur chaque projet.

## 📁 Architecture

```
todo-daily/
├── app/
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── database.py             # SQLite (tables: todos, projects, logs, objectives)
│   ├── models.py               # Modèles Pydantic
│   ├── routers/
│   │   ├── todos.py            # API CRUD todos
│   │   ├── pages.py            # Routes HTML todos
│   │   └── projects.py         # Routes projets (pages + API)
│   ├── services/
│   │   ├── todo_service.py     # Logique todos
│   │   └── project_service.py  # Logique projets (CRUD, weekly, seed)
│   ├── templates/
│   │   ├── base.html           # Layout (navigation ✅ Todo · 🏢 Projets · 📅 Semaine)
│   │   ├── index.html          # Page todos
│   │   └── projects/
│   │       ├── dashboard.html  # Hub projets
│   │       ├── detail.html     # Détail projet + historique
│   │       ├── weekly.html     # Planning hebdo
│   │       ├── _log_list.html  # Partial logs (htmx)
│   │       └── _objective_list.html  # Partial objectifs (htmx)
│   └── static/css/style.css
├── tests/
├── pyproject.toml
└── README.md
```

---

**Built by Ibrahima Xaliloulah Ndiaye** · AMICO TECH · 2026
