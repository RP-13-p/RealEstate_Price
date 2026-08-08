import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from adresse import adresse_vers_coordonnees
from pricing_adjustments import adjust_price, VALID_RENOVATION_STATES

app = FastAPI(title="RealEstate Price API", version="1.0.0")

# Local dev (Vite) + production frontend on Vercel
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://real-estate-price-nine.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loaded once at startup; model/features_list stay None/empty if the artifacts
# are missing, which /api/health then reports. Absolute path since the working
# directory isn't guaranteed to be the project root on every deployment target.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    model = joblib.load(os.path.join(BASE_DIR, 'Training_set', 'best_model.pkl'))
    features_list = joblib.load(os.path.join(BASE_DIR, 'Training_set', 'model_features.pkl'))
except Exception as e:
    print(f"Erreur lors du chargement du modèle: {e}")
    model = None
    features_list = []


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
    ascenseur: bool = True
    etat_renovation: str = "standard"


@app.get("/")
def root():
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
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "features_count": len(features_list) if features_list else 0
    }


@app.get("/api/features")
def get_features():
    if not features_list:
        raise HTTPException(status_code=500, detail="Modèle non chargé")
    return {"success": True, "features": features_list}


@app.post("/api/geocode")
def geocode(request: GeocodeRequest):
    try:
        coords = adresse_vers_coordonnees(
            numero=request.numero,
            rue=request.rue,
            ville=request.ville,
            pays=request.pays
        )
        if coords:
            return {"success": True, "longitude": coords[0], "latitude": coords[1]}
        else:
            raise HTTPException(status_code=404, detail="Adresse non trouvée")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur géolocalisation: {str(e)}")


@app.post("/api/predict")
def predict(request: PredictionRequest):
    """Runs the ML model, then applies elevator/renovation business-rule
    adjustments (see pricing_adjustments.adjust_price) to its raw output."""
    if not model or not features_list:
        raise HTTPException(status_code=500, detail="Modèle non disponible")

    try:
        data = {
            "longitude": request.longitude,
            "latitude": request.latitude,
            "code_postal": request.code_postal,
            "code_type_local": request.code_type_local,
            "lot1_surface_carrez": request.lot1_surface_carrez,
            "nombre_pieces_principales": request.nombre_pieces_principales
        }

        df_input = pd.DataFrame([data])
        missing_features = set(features_list) - set(df_input.columns)
        if missing_features:
            raise HTTPException(status_code=400, detail=f"Features manquantes: {list(missing_features)}")

        df_input = df_input[features_list]
        prediction_ml = model.predict(df_input)[0]

        if request.etat_renovation not in VALID_RENOVATION_STATES:
            raise HTTPException(status_code=400, detail=f"État invalide. Valeurs: {VALID_RENOVATION_STATES}")

        prediction = adjust_price(
            price_ml=prediction_ml,
            ascenseur=request.ascenseur,
            etat_renovation=request.etat_renovation
        )

        prix_m2 = prediction / request.lot1_surface_carrez

        return {
            "success": True,
            "prediction": float(prediction),
            "prediction_formatted": f"{prediction:,.2f} €",
            "prix_m2": float(prix_m2),
            "prix_m2_formatted": f"{prix_m2:,.2f} €/m²",
            "code_postal": request.code_postal
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction: {str(e)}")
