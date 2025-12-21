from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io
from PIL import Image
import torch
import functools
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import numpy as np

# 1. SOLUTION BUG PYTORCH / ULTRALYTICS
torch.load = functools.partial(torch.load, weights_only=False)

# 2. CONFIGURATION FIREBASE
# IMPORTANT : Assure-toi d'avoir uploadé une NOUVELLE clé JSON sur GitHub
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
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_array = np.array(image)
    
    # --- OPTIMISATION POUR LA FOULE ---
    # imgsz=1280 : permet de voir les petits détails (les supporters au loin)
    # conf=0.15 : permet de détecter les personnes même si elles sont partiellement cachées
    results = model(img_array, imgsz=1280, conf=0.15)
    
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
    
    try:
        db.collection("affluence").add(data)
        message = "Données envoyées au Dashboard avec succès"
    except Exception as e:
        message = f"Erreur Firebase : {str(e)}"
                
    return {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "message": message
    }
