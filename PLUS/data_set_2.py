import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

df_metro = pd.read_csv('DATA/metro-france.csv',encoding='utf-8')

df_metro = df_metro[df_metro['Commune nom'].str.contains("Paris")]

df_metro_clean = df_metro.rename(columns={
    "Libelle Line": "ligne",
    "Libelle station": "station",
    "Commune nom": "commune"
})[["ligne", "station", "Longitude", "Latitude", "commune"]]


coords = np.radians(df_metro_clean[["Latitude", "Longitude"]].to_numpy())
tree = BallTree(coords, metric="haversine")

def score_transport(lat, lon):
    """Score basé sur la station la plus proche (rapide avec BallTree)"""
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


# Charger le dataset principal
df = pd.read_csv('DATA/donnees_immobilieres.csv')

df['score_transport'] = np.nan

mask = df['latitude'].notna() & df['longitude'].notna()
df.loc[mask, 'score_transport'] = df[mask].apply(
    lambda row: score_transport(row['latitude'], row['longitude']), 
    axis=1
)
df.to_csv('DATA/donnees_immobilieres.csv', index=False, encoding='utf-8')


