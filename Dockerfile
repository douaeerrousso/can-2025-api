FROM python:3.9-slim

# Installation des dépendances système nécessaires à OpenCV (utilisé par Ultralytics)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ÉTAPE CLÉ : On installe PyTorch version CPU d'abord pour éviter la version lourde (CUDA)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copie et installation du reste des requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ✅ CORRECTION : Utiliser la variable $PORT de Railway (8080)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
