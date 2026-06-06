# 🧠 app/services/todo_service.py
# Logique métier (business logic)
#
# Rôle : contient les vraies opérations sur la base de données
# C'est ici qu'on écrit et lit dans SQLite
#
# Fonctions à créer :
# - get_all_todos(db)     → récupère toutes les tâches
# - create_todo(db, data) → crée une tâche
# - update_todo(db, id)   → marque comme faite / modifie
# - delete_todo(db, id)   → supprime une tâche
#
# Chaque fonction :
# 1. Reçoit la connexion DB et les données
# 2. Exécute la requête SQL
# 3. Renvoie le résultat
#
