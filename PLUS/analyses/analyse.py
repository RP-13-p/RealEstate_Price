import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Charger les données
df = pd.read_csv('DATA/donnees_immobilieres.csv')
df = df.dropna(subset=['latitude', 'longitude', 'valeur_fonciere', 'score_transport', 'prix_m_carrez_arr'])

colonnes_a_exclure = ['valeur_fonciere', 'prix_m_carrez']
X_all = df.drop(columns=colonnes_a_exclure, errors='ignore')
X = X_all.select_dtypes(include=[np.number])
y = df['valeur_fonciere']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Charger le modèle entraîné
model = joblib.load('Training_set/best_model.pkl')
y_pred = model.predict(X_test)

# Calculer les métriques
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
erreurs_relatives = np.abs(y_test - y_pred) / np.abs(y_test) * 100
erreurs_relatives_filtrees = erreurs_relatives[erreurs_relatives <= 100]

print("=" * 60)
print("ANALYSE DES PERFORMANCES DU MODÈLE")
print("=" * 60)
print(f"MAE: {mae:,.0f} €")
print(f"R²: {r2:.4f}")
print(f"Erreur relative moyenne: {erreurs_relatives_filtrees.mean():.2f}%")
print(f"Erreur relative médiane: {np.median(erreurs_relatives_filtrees):.2f}%")
print("=" * 60)
print()

# Créer les visualisations
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Analyse des Performances du Modèle Gradient Boosting', fontsize=16, fontweight='bold')

# 1. Valeurs prédites vs Valeurs réelles
ax1 = axes[0, 0]
ax1.scatter(y_test, y_pred, alpha=0.3, s=10)
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Prédiction parfaite')
ax1.set_xlabel('Valeur Réelle (€)', fontsize=10)
ax1.set_ylabel('Valeur Prédite (€)', fontsize=10)
ax1.set_title(f'Prédictions vs Réalité\nR² = {r2:.4f}', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Distribution des erreurs relatives
ax2 = axes[0, 1]
ax2.hist(erreurs_relatives_filtrees, bins=50, edgecolor='black', alpha=0.7)
ax2.axvline(erreurs_relatives_filtrees.mean(), color='r', linestyle='--', linewidth=2, label=f'Moyenne: {erreurs_relatives_filtrees.mean():.2f}%')
ax2.axvline(np.median(erreurs_relatives_filtrees), color='g', linestyle='--', linewidth=2, label=f'Médiane: {np.median(erreurs_relatives_filtrees):.2f}%')
ax2.set_xlabel('Erreur Relative (%)', fontsize=10)
ax2.set_ylabel('Fréquence', fontsize=10)
ax2.set_title('Distribution des Erreurs Relatives', fontsize=12)
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Importance des features
ax3 = axes[1, 0]
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=True)
ax3.barh(feature_importance['feature'], feature_importance['importance'])
ax3.set_xlabel('Importance', fontsize=10)
ax3.set_ylabel('Features', fontsize=10)
ax3.set_title('Importance des Features', fontsize=12)
ax3.grid(True, alpha=0.3, axis='x')

# 4. Résidus
ax4 = axes[1, 1]
residus = y_test - y_pred
ax4.scatter(y_pred, residus, alpha=0.3, s=10)
ax4.axhline(y=0, color='r', linestyle='--', lw=2)
ax4.set_xlabel('Valeurs Prédites (€)', fontsize=10)
ax4.set_ylabel('Résidus (€)', fontsize=10)
ax4.set_title(f'Analyse des Résidus\nMAE = {mae:,.0f} €', fontsize=12)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('analyse_performances.png', dpi=300, bbox_inches='tight')
print("✓ Graphiques sauvegardés: analyse_performances.png")
plt.show()
