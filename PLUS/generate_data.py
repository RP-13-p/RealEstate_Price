import numpy as np
import pandas as pd


# Fixer la graine pour avoir toujours les mêmes données
np.random.seed(42)

# Nombre de lignes
n = 50000

#Creation de données aléatoires
ids = list(range(1, n + 1))
latitude = list(np.random.uniform(41,51,size=n))
longitude = list(np.random.uniform(-5,9,size=n))
#Lorsque le user entrera l'adresse je ferais appel a une API qui détermineras ses coordonées
prix = list(np.random.uniform(100000,1000000, size = n))
surface = list(np.random.uniform(15,150,size=n))
nb_pieces = list(np.random.randint(1,5,size=n))
nb_chambres = list(np.random.randint(0,4,size=n))
etage = list(np.random.randint(0,10,size=n))
annee_construction = list(np.random.randint(1950,2024,size=n))
biens = ["appartement","maison"]
type_bien = [biens[np.random.randint(0,2)] for i in range(n)]
presence_balcon = list(np.random.randint(0,1,size=n))
presence_parking =list(np.random.randint(0,1,size=n))
distance_transport = list(np.random.uniform(0.01,2,size=n))




# TODO : Créer le DataFrame
df = pd.DataFrame({
    'id': ids,
    'latitude':latitude,
    'longitude':longitude,
    'prix':prix,
    'surface':surface,
    'nb_pieces':nb_pieces,
    'nb_chambres':nb_chambres,
    'etage':etage,
    'annee_construction':annee_construction,
    'type_bien':type_bien,
    'presence_balcon':presence_balcon,
    'presence_parking':presence_parking,
    'distance_transport':distance_transport

})

# TODO : Sauvegarder en CSV
df.to_csv('donnees_immobilieres.csv', index=False, encoding='utf-8')
print(f"Fichier créé avec {len(df)} lignes")

