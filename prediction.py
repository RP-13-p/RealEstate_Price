import pandas as pd
import numpy as np
import joblib



model = joblib.load('Training_set/best_model.pkl')
features_list = joblib.load('Training_set/model_features.pkl')


def predire_valeur_fonciere(input_data):
    """
    Prédit la valeur foncière d'un bien immobilier
    
    Parameters:
    -----------
    input_data : dict ou pd.DataFrame
        Les caractéristiques du bien immobilier
        Doit contenir toutes les features utilisées lors de l'entraînement
    
    Returns:
    --------
    float : La valeur foncière prédite en euros
    """
    # Convertir en DataFrame si nécessaire
    if isinstance(input_data, dict):
        df_input = pd.DataFrame([input_data])
    else:
        df_input = input_data.copy()
    
    # Vérifier que toutes les features nécessaires sont présentes
    missing_features = set(features_list) - set(df_input.columns)
    if missing_features:
        raise ValueError(f"Features manquantes: {missing_features}")
    
    df_input = df_input[features_list]
    # Faire la prédiction
    prediction = model.predict(df_input)
    
    return prediction[0] if len(prediction) == 1 else prediction

