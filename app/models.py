# 📐 app/models.py
# Modèles de données (Pydantic)
#
# Rôle : définir la STRUCTURE des données qu'on manipule
# Pydantic valide automatiquement ce qui entre et sort de l'API
#
# Schémas à créer :
# - TodoCreate → ce que le client envoie pour créer une tâche
#   (title: str, priority: str)
# - TodoUpdate → ce qu'on peut modifier
#   (title: str | None, completed: bool | None, priority: str | None)
# - TodoResponse → ce qu'on renvoie au client
#   (id, title, completed, priority, created_at)
#
