from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io
from PIL import Image
import torch
import functools
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 1. SOLUTION BUG PYTORCH / ULTRALYTICS
# Cette ligne est indispensable pour charger le modèle sur Koyeb
torch.load = functools.partial(torch.load, weights_only=False)

# 2. CONFIGURATION FIREBASE (PaaS Stockage)
# Charge la clé JSON que tu as ajoutée sur GitHub
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# 3. CHARGEMENT DU MODÈLE IA
# Le modèle Nano est idéal pour les ressources gratuites de Koyeb
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
    """
    Cette route reçoit une image et le nom du stade, 
    compte les supporters et sauvegarde le résultat.
    """
    # Lecture de l'image envoyée
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes))
    
    # Inférence IA avec YOLO
    results = model(image)
    
    # Comptage des personnes (la classe '0' dans YOLO est 'person')
    count = 0
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0: 
                count += 1
    
    # 4. SAUVEGARDE EN TEMPS RÉEL DANS FIREBASE
    data = {
        "stade": stade_name,
        "nombre_supporters": count,
        "timestamp": datetime.now() # Heure précise pour le Dashboard
    }
    
    # Enregistre dans la collection 'affluence' sur Firestore
    db.collection("affluence").add(data)
                
    return {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "message": "Données envoyées au Dashboard avec succès"
    }
