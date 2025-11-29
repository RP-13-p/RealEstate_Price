from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from adresse import adresse_vers_coordonnees
import os

app = Flask(__name__)

# Charger le modèle et les features
model = joblib.load('Training_set/best_model.pkl')
features_list = joblib.load('Training_set/model_features.pkl')


@app.route('/')
def index():
    """Page d'accueil avec le formulaire"""
    return render_template('index.html', features=features_list)


@app.route('/geocode', methods=['POST'])
def geocode():
    """
    Endpoint pour convertir une adresse en coordonnées GPS
    """
    try:
        data = request.json
        numero = data.get('numero', '')
        rue = data.get('rue', '')
        ville = data.get('ville', '')
        pays = data.get('pays', 'France')
        
        coords = adresse_vers_coordonnees(numero, rue, ville, pays)
        
        if coords:
            return jsonify({
                'success': True,
                'longitude': coords[0],
                'latitude': coords[1]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Adresse non trouvée'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint pour faire une prédiction de valeur foncière
    """
    try:
        data = request.json
        
        # Créer un DataFrame avec les données d'entrée
        df_input = pd.DataFrame([data])
        
        # Vérifier que toutes les features nécessaires sont présentes
        missing_features = set(features_list) - set(df_input.columns)
        if missing_features:
            return jsonify({
                'success': False,
                'message': f'Features manquantes: {list(missing_features)}'
            }), 400
        
        # Réordonner les colonnes selon l'ordre du modèle
        df_input = df_input[features_list]
        
        # Faire la prédiction
        prediction = model.predict(df_input)[0]
        
        return jsonify({
            'success': True,
            'prediction': float(prediction),
            'prediction_formatted': f"{prediction:,.2f} €"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/features', methods=['GET'])
def get_features():
    """
    Retourne la liste des features nécessaires pour la prédiction
    """
    return jsonify({
        'success': True,
        'features': features_list
    })


if __name__ == '__main__':
    # Vérifier que les fichiers du modèle existent
    if not os.path.exists('Training_set/best_model.pkl'):
        print("ERREUR: Le fichier 'Training_set/best_model.pkl' n'existe pas.")
        print("Veuillez d'abord entraîner le modèle avec model/model.py")
        exit(1)
    
    if not os.path.exists('Training_set/model_features.pkl'):
        print("ERREUR: Le fichier 'Training_set/model_features.pkl' n'existe pas.")
        print("Veuillez d'abord entraîner le modèle avec model/model.py")
        exit(1)
    
    print("\n" + "="*60)
    print("Application Web d'Estimation Immobilière")
    print("="*60)
    print("\nLe serveur démarre sur: http://127.0.0.1:5000")
    print("Ouvrez cette URL dans votre navigateur.\n")
    print("Appuyez sur Ctrl+C pour arrêter le serveur.")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
