import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from supabase import create_client, Client
import io, torch, functools
from PIL import Image
import numpy as np
import uvicorn

# Fix technique pour charger le modèle YOLO sur Railway/Koyeb
torch.load = functools.partial(torch.load, weights_only=False)

# --- CONFIGURATION SUPABASE ---
# Utilisation de la clé publishable confirmée dans tes captures
SUPABASE_URL = "https://qpwwceigajtigvhpmbpg.supabase.co"
SUPABASE_KEY = "sb_publishable_hYAcKlZbCfCdW-SzdiEIDA_Ng7jGwO7"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ✅ MIDDLEWARE CORS (Indispensable pour React/Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle YOLOv8
print("🚀 Chargement du modèle YOLOv8...")
try:
    model = YOLO('yolov8n.pt')
    print("✅ Modèle YOLOv8 chargé avec succès")
except Exception as e:
    print(f"❌ Erreur chargement modèle: {e}")
    model = None

@app.get("/")
def home():
    return {"status": "IA active", "database": "Supabase Connected", "model": "YOLOv8n"}

@app.post("/predict")
async def predict(stade_name: str = Form(...), file: UploadFile = File(...)):
    try:
        if model is None:
            return {"error": "Modèle non disponible"}, 500
        
        # Lire et convertir l'image
        img_bytes = await file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        # Détection (Optimisée pour CPU sur Railway)
        results = model(np.array(image), imgsz=640, conf=0.25) # imgsz réduit pour économiser la RAM
        count = sum(len(r.boxes) for r in results)
        
        # Envoi à Supabase (Table: affluence)
        data = {
            "stade": stade_name, 
            "nombre_supporters": count
        }
        
        supabase.table("affluence").insert(data).execute()
        
        return {
            "stade": stade_name, 
            "nombre_supporters": count, 
            "status": "Success"
        }
    
    except Exception as e:
        return {"error": str(e)}, 500

# ✅ LANCEMENT DU SERVEUR (Correctif Railway)
if __name__ == "__main__":
    # Railway injecte automatiquement le port nécessaire via la variable PORT
    port = int(os.getenv("PORT", 8000))
    print(f"🔥 Serveur en cours d'exécution sur le port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
