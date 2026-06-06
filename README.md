# Todo-Daily

Application de todo list quotidienne pour organiser vos journées efficacement.

## Stack

- Python 3.11+
- FastAPI
- SQLite
- Jinja2 + htmx
- Tailwind CSS v4
- UV

## Architecture

```
todo-daily/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Connexion SQLite + création des tables
│   ├── models.py            # Modèles Pydantic (validation des données)
│   ├── routers/
│   │   ├── todos.py         # API CRUD des todos (JSON)
│   │   └── pages.py         # Routes HTML (pages web)
│   ├── services/
│   │   └── todo_service.py  # Logique métier (business logic)
│   ├── templates/
│   │   ├── base.html        # Layout commun (navbar, footer)
│   │   ├── index.html       # Page principale
│   │   └── components/      # Petits bouts de HTML réutilisables
│   └── static/
│       └── css/
│           └── style.css    # Styles Tailwind personnalisés
├── tests/
│   └── test_todos.py        # Tests de l'application
├── pyproject.toml            # Configuration UV + dépendances
├── .gitignore                # Fichiers à ignorer par Git
└── README.md                 # Ce fichier
```
