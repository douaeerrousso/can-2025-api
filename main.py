import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from supabase import create_client, Client
import io, torch, functools
from PIL import Image
import numpy as np
import uvicorn

# Fix technique pour charger le modèle YOLO sur Railway
torch.load = functools.partial(torch.load, weights_only=False)

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = "https://qpwwceigajtigvhpmbpg.supabase.co"
SUPABASE_KEY = "sb_publishable_hYAcKlZbCfCdW-SzdiEIDA_Ng7jGwO7"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ✅ MIDDLEWARE CORS - TRÈS IMPORTANT POUR LE FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle YOLOv8
model = YOLO('yolov8n.pt') 

@app.get("/")
def home():
    return {"status": "IA active", "database": "Supabase"}

# ✅ CORRECTION : Ajouter Form() pour les paramètres FormData
@app.post("/predict")
async def predict(stade_name: str = Form(...), file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        # Détection des supporters avec YOLOv8
        results = model(np.array(image), imgsz=1280, conf=0.05)
        count = sum(len(r.boxes) for r in results)
        
        # Envoi direct des données à Supabase
        data = {
            "stade": stade_name, 
            "nombre_supporters": count
            # La colonne 'timestamp' se remplira toute seule avec now()
        }
        
        try:
            supabase.table("affluence").insert(data).execute()
            db_status = "Succès Supabase"
        except Exception as e:
            db_status = f"Erreur : {str(e)}"
                    
        return {
            "stade": stade_name, 
            "nombre_supporters": count, 
            "database": db_status
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "stade": stade_name,
            "database": "Erreur lors du traitement"
        }

# ✅ POINT D'ENTRÉE - Gère le PORT de Railway automatiquement
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
