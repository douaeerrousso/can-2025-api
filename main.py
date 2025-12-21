from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import io
from PIL import Image
import torch
import functools

# Solution radicale pour le bug PyTorch/Ultralytics
# On redéfinit temporairement le chargement pour accepter le modèle YOLO
torch.load = functools.partial(torch.load, weights_only=False)

app = FastAPI()

# Chargement du modèle
model = YOLO('yolov8n.pt') 

@app.get("/")
def home():
    return {"message": "API CAN 2025 opérationnelle !"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
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
