import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

df_v1 = pd.read_csv('DATA/dvf.csv', encoding='utf-8')
print(df_v1.columns)

df_clean = df_v1[[
    "date_mutation",
    "valeur_fonciere",
    "longitude",
    "latitude",
    "code_postal",
    "code_type_local",
    "nom_commune",
    "lot1_surface_carrez",
    "nombre_pieces_principales",
    "type_local",
    "nature_mutation",
]]

df_clean = df_clean.drop_duplicates()
necessary_data = ["valeur_fonciere", "longitude", "latitude", "lot1_surface_carrez", "nombre_pieces_principales"]
df_clean = df_clean.dropna(subset=necessary_data)
df_clean = df_clean[df_clean["nombre_pieces_principales"] != 0]

cols_float = ["valeur_fonciere", "longitude", "latitude", "lot1_surface_carrez"]
df_clean[cols_float] = df_clean[cols_float].apply(pd.to_numeric, errors="coerce")

cols_int = ["nombre_pieces_principales", "code_type_local", "code_postal"]
df_clean[cols_int] = df_clean[cols_int].apply(pd.to_numeric, errors='coerce').astype('Int64')

df_clean["date_mutation"] = pd.to_datetime(df_clean["date_mutation"], errors="coerce")

df_clean['prix_m_carrez'] = df_clean['valeur_fonciere'] / df_clean['lot1_surface_carrez']
df_clean = df_clean.sort_values('date_mutation')
df_clean = df_clean[~df_clean['code_type_local'].isin([1, 3, 4])]

df_metro = pd.read_csv('DATA/metro-france.csv', encoding='utf-8')
df_metro = df_metro[df_metro['Commune nom'].str.contains("Paris")]
df_metro_clean = df_metro.rename(columns={
    "Libelle Line": "ligne",
    "Libelle station": "station",
    "Commune nom": "commune"
})[["ligne", "station", "Longitude", "Latitude", "commune"]]

coords = np.radians(df_metro_clean[["Latitude", "Longitude"]].to_numpy())
tree = BallTree(coords, metric="haversine")

def score_transport(lat, lon):
    point = np.radians([[lat, lon]])
    dist, _ = tree.query(point, k=1)  
    d_km = dist[0][0] * 6371 
    if d_km < 0.150: 
        return 5
    if d_km < 0.400: 
        return 4
    if d_km < 0.800: 
        return 3
    if d_km < 1.500: 
        return 2
    return 1

df_clean['score_transport'] = np.nan
mask = df_clean['latitude'].notna() & df_clean['longitude'].notna()
df_clean.loc[mask, 'score_transport'] = df_clean[mask].apply(lambda row: score_transport(row['latitude'], row['longitude']), axis=1)

prix_moyen_par_arrondissement = df_clean.groupby('code_postal')['prix_m_carrez'].mean().to_dict()
df_clean['prix_m_carrez_arr'] = df_clean['code_postal'].map(prix_moyen_par_arrondissement)

# Suppression des prix exorbitants (>50% de la moyenne de l'arrondissement)
seuil_max = 1.50  # 150% de la moyenne de l'arrondissement
df_clean['ratio_prix'] = df_clean['prix_m_carrez'] / df_clean['prix_m_carrez_arr']
nb_avant = len(df_clean)
df_clean = df_clean[df_clean['ratio_prix'] <= seuil_max]
df_clean = df_clean.drop(columns=['ratio_prix'])


print(df_clean["score_transport"].value_counts())
df_clean.to_csv('DATA/donnees_immobilieres.csv', index=False, encoding='utf-8')
