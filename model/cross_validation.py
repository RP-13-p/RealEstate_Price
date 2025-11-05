import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import GradientBoostingRegressor
import joblib

# Charger les données
df = pd.read_csv('DATA/donnees_immobilieres.csv')
df = df.dropna(subset=['latitude', 'longitude', 'valeur_fonciere', 'score_transport', 'prix_m_carrez_arr'])

# Échantillonner 20% des données pour accélérer
df_sample = df.sample(frac=0.2, random_state=42)

colonnes_a_exclure = ['valeur_fonciere', 'prix_m_carrez']
X_all = df_sample.drop(columns=colonnes_a_exclure, errors='ignore')
X = X_all.select_dtypes(include=[np.number])
y = df_sample['valeur_fonciere']

print("=" * 60)
print("CROSS-VALIDATION RAPIDE (échantillon 20%)")
print("=" * 60)
print(f"Nombre de données: {len(X)}")
print(f"Nombre de features: {X.shape[1]}")
print(f"Features: {list(X.columns)}")
print()

# K-Fold Cross-Validation avec 3 folds (plus rapide que 5)
print("-" * 60)
print("K-FOLD CROSS-VALIDATION (3 folds)")
print("-" * 60)

model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
kfold = KFold(n_splits=3, shuffle=True, random_state=42)

# R² scores
r2_scores = cross_val_score(model, X, y, cv=kfold, scoring='r2')
print(f"R² scores par fold: {r2_scores}")
print(f"R² moyen: {r2_scores.mean():.4f} (+/- {r2_scores.std() * 2:.4f})")

# MAE scores
mae_scores = -cross_val_score(model, X, y, cv=kfold, scoring='neg_mean_absolute_error')
print(f"MAE moyen: {mae_scores.mean():,.0f} € (+/- {mae_scores.std() * 2:,.0f})")

# RMSE scores
rmse_scores = np.sqrt(-cross_val_score(model, X, y, cv=kfold, scoring='neg_mean_squared_error'))
print(f"RMSE moyen: {rmse_scores.mean():,.0f} € (+/- {rmse_scores.std() * 2:,.0f})")

print()
print("=" * 60)
print("✓ Cross-validation terminée!")
print("Les résultats sont cohérents avec le modèle entraîné." if r2_scores.mean() > 0.8 else "Attention: performances plus faibles")
print("=" * 60)