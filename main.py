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

# ✅ MIDDLEWARE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle YOLOv8
print(" Chargement du modèle YOLOv8...")
try:
    model = YOLO('yolov8n.pt')
    print(" Modèle YOLOv8 chargé avec succès")
except Exception as e:
    print(f" Erreur lors du chargement du modèle: {e}")
    model = None

@app.get("/")
def home():
    return {"status": "IA active", "database": "Supabase", "model": "YOLOv8n"}

@app.post("/predict")
async def predict(stade_name: str = Form(...), file: UploadFile = File(...)):
    try:
        print(f"📥 Reçu: stade={stade_name}, fichier={file.filename}")
        
        if model is None:
            return {"error": "Modèle YOLOv8 non chargé", "stade": stade_name}, 500
        
        # Lire l'image
        img_bytes = await file.read()
        print(f"📦 Taille de l'image: {len(img_bytes)} bytes")
        
        # Vérifier que c'est une image valide
        try:
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            print(f" Image chargée: {image.size}")
        except Exception as e:
            print(f" Erreur lors du chargement de l'image: {e}")
            return {"error": f"Image invalide: {str(e)}", "stade": stade_name}, 400
        
        # Détection avec YOLOv8
        print(" Analyse YOLOv8 en cours...")
        try:
            results = model(np.array(image), imgsz=1280, conf=0.05)
            count = sum(len(r.boxes) for r in results)
            print(f" Détection complète: {count} supporters détectés")
        except Exception as e:
            print(f" Erreur lors de la détection: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Erreur YOLOv8: {str(e)}", "stade": stade_name}, 500
        
        # Envoi à Supabase
        data = {
            "stade": stade_name, 
            "nombre_supporters": count
        }
        
        db_status = "Succès Supabase"
        try:
            print(f" Envoi à Supabase: {data}")
            supabase.table("affluence").insert(data).execute()
            print(" Données insérées dans Supabase")
        except Exception as e:
            db_status = f"Erreur Supabase: {str(e)}"
            print(f" {db_status}")
        
        return {
            "stade": stade_name, 
            "nombre_supporters": count, 
            "database": db_status
        }
    
    except Exception as e:
        print(f" ERREUR GÉNÉRALE: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "stade": stade_name,
            "database": "Erreur lors du traitement"
        }, 500

# ✅ LANCER LE SERVEUR DIRECTEMENT (sans if __name__)
# Railway va exécuter ce code au démarrage
port = int(os.getenv("PORT", 8000))
print(f"🚀 Démarrage du serveur sur le port {port}")
uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
