# 🔌 app/routers/todos.py
# API REST des todos
#
# Rôle : exposer les endpoints JSON pour le CRUD
# Ces routes sont appelées par htmx côté frontend
#
# Routes à créer :
# - GET    /api/todos      → liste toutes les tâches
# - POST   /api/todos      → crée une nouvelle tâche
# - PUT    /api/todos/{id} → modifie une tâche
# - DELETE /api/todos/{id} → supprime une tâche
#
# Chaque fonction :
# 1. Reçoit la requête
# 2. Appelle le service
# 3. Renvoie la réponse (JSON ou HTML)
#
