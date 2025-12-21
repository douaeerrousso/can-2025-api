from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io, os, json, torch, functools, firebase_admin
from PIL import Image
from firebase_admin import credentials, firestore
from datetime import datetime
import numpy as np

# Correction bug chargement modèle
torch.load = functools.partial(torch.load, weights_only=False)

# Connexion Firebase via une variable système (plus fiable)
if not firebase_admin._apps:
    key_data = json.loads(os.getenv("FIREBASE_KEY"))
    cred = credentials.Certificate(key_data)
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()
model = YOLO('yolov8n.pt') 

@app.post("/predict")
async def predict(stade_name: str, file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    
    # Analyse haute précision pour la foule
    results = model(np.array(image), imgsz=1280, conf=0.15)
    
    count = sum(1 for result in results for box in result.boxes if int(box.cls[0]) == 0)
    
    data = {"stade": stade_name, "nombre_supporters": count, "timestamp": datetime.now()}
    db.collection("affluence").add(data)
                
    return {"stade": stade_name, "nombre_supporters": count, "status": "Succès !"}
