from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
from supabase import create_client, Client
import io, torch, functools
from PIL import Image
import numpy as np

# Fix technique pour charger le modèle YOLO sur Koyeb
torch.load = functools.partial(torch.load, weights_only=False)

# --- CONFIGURATION SUPABASE ---
# Trouve ces infos dans Supabase -> Settings -> API
SUPABASE_URL = "https://qpwwceigajtigvhpmbpg.supabase.co"
SUPABASE_KEY = "sb_publishable_hYAcKlZbCfCdW-SzdiEIDA_Ng7jGwO7"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()
model = YOLO('yolov8n.pt') 

@app.get("/")
def home():
    return {"status": "IA active", "database": "Supabase"}

@app.post("/predict")
async def predict(stade_name: str, file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    
    # Détection des supporters (Ton modèle voit 75 personnes !)
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
        db_status = " Succès Supabase"
    except Exception as e:
        db_status = f" Erreur : {str(e)}"
                
    return {
        "stade": stade_name, 
        "nombre_supporters": count, 
        "database": db_status
    }
