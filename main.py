from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io, os, json, torch, functools, firebase_admin
from PIL import Image
from firebase_admin import credentials, firestore
from datetime import datetime
import numpy as np

# 1. FIX TECHNIQUE
torch.load = functools.partial(torch.load, weights_only=False)

# 2. NETTOYAGE AUTOMATIQUE DE LA CLÉ FIREBASE
if not firebase_admin._apps:
    try:
        # Récupère la clé brute de Koyeb
        raw_key = os.getenv("FIREBASE_KEY")
        key_dict = json.loads(raw_key)
        
        # RÉPARATION CRITIQUE : Nettoie les retours à la ligne de la clé privée
        if "private_key" in key_dict:
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Erreur Config: {e}")

db = firestore.client()
app = FastAPI()
model = YOLO('yolov8n.pt') 

@app.post("/predict")
async def predict(stade_name: str, file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    
    # Paramètres optimisés pour compter un maximum de personnes (75+ détectés !)
    results = model(np.array(image), imgsz=1280, conf=0.05)
    
    count = 0
    for result in results:
        count += len(result.boxes)
    
    data = {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "timestamp": datetime.now()
    }
    
    # Tentative d'envoi à Firebase
    try:
        db.collection("affluence").add(data)
        res_msg = "✅ Enregistré avec succès dans Firebase !"
    except Exception as e:
        # Si ça échoue encore, on affiche l'erreur pour comprendre
        res_msg = f"❌ Erreur Firebase: {str(e)}"
                
    return {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "status": res_msg
    }
