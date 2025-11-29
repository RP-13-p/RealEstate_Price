from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from adresse import adresse_vers_coordonnees
import uvicorn
import os

# Créer l'application FastAPI
app = FastAPI(title="RealEstate Price API", version="1.0.0")

# Configuration CORS pour permettre les requêtes depuis React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Ports React/Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle
try:
    model = joblib.load('Training_set/best_model.pkl')
    features_list = joblib.load('Training_set/model_features.pkl')
    print("✓ Modèle chargé avec succès")
except Exception as e:
    print(f"⚠️ Erreur lors du chargement du modèle: {e}")
    model = None
    features_list = []


# Modèles Pydantic pour la validation
class GeocodeRequest(BaseModel):
    numero: str = ""
    rue: str
    ville: str
    pays: str = "France"


class PredictionRequest(BaseModel):
    longitude: float
    latitude: float
    code_postal: int
    code_type_local: int
    lot1_surface_carrez: float
    nombre_pieces_principales: int


@app.get("/")
def root():
    """Point d'entrée de l'API"""
    return {
        "message": "RealEstate Price API",
        "version": "1.0.0",
        "endpoints": {
            "geocode": "/api/geocode",
            "predict": "/api/predict",
            "features": "/api/features",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "features_count": len(features_list) if features_list else 0
    }


@app.get("/api/features")
def get_features():
    """Retourne la liste des features nécessaires"""
    if not features_list:
        raise HTTPException(status_code=500, detail="Modèle non chargé")
    
    return {
        "success": True,
        "features": features_list
    }


@app.post("/api/geocode")
def geocode(request: GeocodeRequest):
    """Convertit une adresse en coordonnées GPS"""
    try:
        coords = adresse_vers_coordonnees(
            numero=request.numero,
            rue=request.rue,
            ville=request.ville,
            pays=request.pays
        )
        
        if coords:
            return {
                "success": True,
                "longitude": coords[0],
                "latitude": coords[1]
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Adresse non trouvée"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la géolocalisation: {str(e)}"
        )


@app.post("/api/predict")
def predict(request: PredictionRequest):
    """Prédit la valeur foncière d'un bien"""
    if not model or not features_list:
        raise HTTPException(
            status_code=500,
            detail="Modèle non disponible. Veuillez d'abord entraîner le modèle."
        )
    
    try:
        # Créer un DataFrame avec les données
        data = {
            "longitude": request.longitude,
            "latitude": request.latitude,
            "code_postal": request.code_postal,
            "code_type_local": request.code_type_local,
            "lot1_surface_carrez": request.lot1_surface_carrez,
            "nombre_pieces_principales": request.nombre_pieces_principales
        }
        
        df_input = pd.DataFrame([data])
        
        # Vérifier les features manquantes
        missing_features = set(features_list) - set(df_input.columns)
        if missing_features:
            raise HTTPException(
                status_code=400,
                detail=f"Features manquantes: {list(missing_features)}"
            )
        
        # Réordonner selon le modèle
        df_input = df_input[features_list]
        
        # Prédiction
        prediction = model.predict(df_input)[0]
        
        return {
            "success": True,
            "prediction": float(prediction),
            "prediction_formatted": f"{prediction:,.2f} €"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )


if __name__ == "__main__":
    # Vérifier l'existence du modèle
    if not os.path.exists('Training_set/best_model.pkl'):
        print("\n" + "="*60)
        print("⚠️  ERREUR: Le modèle n'existe pas")
        print("="*60)
        print("\nVeuillez d'abord entraîner le modèle:")
        print("  cd model")
        print("  python model.py")
        print("\n" + "="*60 + "\n")
        exit(1)
    
    print("\n" + "="*60)
    print("🚀 API RealEstate Price")
    print("="*60)
    print("\nAPI démarrée sur: http://127.0.0.1:8000")
    print("Documentation interactive: http://127.0.0.1:8000/docs")
    print("\nEndpoints disponibles:")
    print("  • GET  /api/health   - État de l'API")
    print("  • GET  /api/features - Liste des features")
    print("  • POST /api/geocode  - Géolocalisation")
    print("  • POST /api/predict  - Prédiction")
    print("\nAppuyez sur Ctrl+C pour arrêter.")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
