import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

df = pd.read_csv('../DATA/donnees_immobilieres.csv')
df = df.dropna(subset=['latitude', 'longitude', 'valeur_fonciere', 'score_transport', 'prix_m_carrez_arr'])

# Exclure les colonnes liées au prix car elles ne doivent pas être des features d'entrée
colonnes_a_exclure = ['valeur_fonciere', 'prix_m_carrez', 'prix_m_carrez_arr', 'score_transport']
X_all = df.drop(columns=colonnes_a_exclure, errors='ignore')
X = X_all.select_dtypes(include=[np.number])
y = df['valeur_fonciere']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

gb_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
gb_model.fit(X_train, y_train)
y_pred = gb_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(r2)
print(mae)


joblib.dump(gb_model, '../Training_set/best_model.pkl')
joblib.dump(list(X.columns), '../Training_set/model_features.pkl')




