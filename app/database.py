# 🗄️ app/database.py
# Gestion de la base de données SQLite
#
# Rôle : créer et gérer la connexion à la base SQLite
#
# Une todo list a besoin d'une table "todos" avec :
# - id (numéro unique auto-généré)
# - title (texte de la tâche)
# - completed (est-ce fait ? vrai/faux)
# - created_at (date de création)
# - priority (priorité : haute/moyenne/basse)
#
# Fonctions à créer :
# - get_db() → donne une connexion à la base
# - init_db() → crée les tables si elles n'existent pas
#
