# Utilise une image Python officielle
FROM python:3.13-slim

# Crée un répertoire dans le conteneur
WORKDIR /app

# Copie tout le contenu dans le conteneur
COPY . .

# Installe les dépendances si tu en as
RUN pip install --no-cache-dir -r requirements.txt

# Commande exécutée au lancement du conteneur
CMD ["python", "main.py"]
