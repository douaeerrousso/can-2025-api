from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io
from PIL import Image
import torch
import functools
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import numpy as np  # <--- MODIFICATION 1 : Ajouter cet import

# 1. SOLUTION BUG PYTORCH / ULTRALYTICS
torch.load = functools.partial(torch.load, weights_only=False)

# 2. CONFIGURATION FIREBASE
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# 3. CHARGEMENT DU MODÈLE IA
model = YOLO('yolov8n.pt') 

@app.get("/")
def home():
    return {
        "projet": "Gestion Affluence CAN 2025",
        "status": "Opérationnel",
        "database": "Connectée à Firebase"
    }

@app.post("/predict")
async def predict(stade_name: str, file: UploadFile = File(...)):
    # Lecture de l'image
    img_bytes = await file.read()
    
    # MODIFICATION 2 : Convertir en RGB pour éviter les erreurs avec les images PNG/RGBA
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    
    # MODIFICATION 3 : Convertir l'image en tableau Numpy
    # C'est ce qui règle définitivement l'erreur "FileNotFoundError" sur Koyeb
    img_array = np.array(image)
    
    # Lancer la détection sur le tableau d'image
    results = model(img_array)
    
    count = 0
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0: 
                count += 1
    
    # 4. SAUVEGARDE DANS FIREBASE
    data = {
        "stade": stade_name,
        "nombre_supporters": count,
        "timestamp": datetime.now()
    }
    
    db.collection("affluence").add(data)
                
    return {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "message": "Données envoyées au Dashboard avec succès"
    }
