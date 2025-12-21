# Utilise Python
FROM python:3.9-slim

# Installe des outils nécessaires pour l'image
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installe les outils de requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code
COPY . .

# Lance l'API sur le port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
