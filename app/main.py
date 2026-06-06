# 🚀 app/main.py
# Point d'entrée de l'application FastAPI
#
# C'est LE fichier qui démarre tout :
# 1. Crée l'instance FastAPI
# 2. Monte les fichiers statiques (CSS)
# 3. Configure Jinja2 (moteur de templates HTML)
# 4. Enregistre les routers (liens vers les autres fichiers)
# 5. Démarre le serveur avec uvicorn
#
# Commandes pour lancer l'app :
#   uv run uvicorn app.main:app --reload
#
