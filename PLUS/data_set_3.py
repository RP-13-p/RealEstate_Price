import pandas as pd
import numpy as np

# Charger le dataset
df = pd.read_csv('DATA/donnees_immobilieres.csv')

# Calculer le prix_m_carrez moyen par code postal
prix_moyen_par_arrondissement = df.groupby('code_postal')['prix_m_carrez'].mean().to_dict()

# Créer la colonne prix_m_carrez_arr en mappant les codes postaux
df['prix_m_carrez_arr'] = df['code_postal'].map(prix_moyen_par_arrondissement)

# Sauvegarder le dataset mis à jour
df.to_csv('DATA/donnees_immobilieres.csv', index=False, encoding='utf-8')


