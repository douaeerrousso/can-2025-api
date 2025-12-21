from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io
from PIL import Image
import torch

# CETTE LIGNE EST LA CLÉ : Elle autorise PyTorch à charger le modèle YOLO
torch.serialization.add_safe_globals(["ultralytics.nn.tasks.DetectionModel"])

app = FastAPI()

# Chargement du modèle (il se téléchargera automatiquement au premier lancement)
model = YOLO('yolov8n.pt') 

@app.get("/")
def home():
    return {"message": "API CAN 2025 opérationnelle !"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Lire l'image
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes))
    
    # Lancer la détection
    results = model(image)
    
    # Compter uniquement les personnes (classe 0)
    count = 0
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0: 
                count += 1
                
    return {"stade": "Rabat", "nombre_supporters": count}
