from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io, os, json, torch, functools, firebase_admin
from PIL import Image
from firebase_admin import credentials, firestore
from datetime import datetime
import numpy as np

# 1. FIX CHARGEMENT
torch.load = functools.partial(torch.load, weights_only=False)

# 2. CONNEXION FIREBASE (CORRIGÉE POUR LES \n)
if not firebase_admin._apps:
    raw_key = os.getenv("FIREBASE_KEY")
    # Ce code remplace les mauvais caractères de signature
    key_dict = json.loads(raw_key, strict=False)
    if "\\n" in key_dict["private_key"]:
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
    
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()
model = YOLO('yolov8n.pt') 

@app.post("/predict")
async def predict(stade_name: str, file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    
    # --- DETECTION MAXIMALE ---
    # On baisse la confiance à 0.05 pour détecter plus de monde
    results = model(np.array(image), imgsz=1280, conf=0.05)
    
    count = 0
    for result in results:
        count += len(result.boxes) # Compte tous les objets détectés
    
    data = {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "timestamp": datetime.now()
    }
    
    try:
        db.collection("affluence").add(data)
        res_msg = "Enregistré dans Firebase !"
    except Exception as e:
        res_msg = f"Erreur database: {str(e)}"
                
    return {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "message": res_msg
    }
