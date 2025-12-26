FROM python:3.9-slim

# Installation des dépendances système nécessaires à OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation de PyTorch CPU (version légère)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copie et installation des requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ✅ SOLUTION : Lancer Python directement (pas besoin de sh -c)
# Python gérera le PORT lui-même dans main.py
CMD ["python", "main.py"]
