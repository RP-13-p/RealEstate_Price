import pandas as pd

df_v1= pd.read_csv('DATA/dvf.csv', encoding='utf-8')


#On garde que les données utiles 

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

#Supresssion doublons,des lignes inutilisables
df_clean = df_clean.drop_duplicates()
necessary_data = ["valeur_fonciere","longitude","latitude","lot1_surface_carrez","nombre_pieces_principales"]
df_clean = df_clean.dropna(subset=necessary_data)
df_clean = df_clean.dropna(subset=necessary_data)

df_clean = df_clean[df_clean["nombre_pieces_principales"] != 0]
cols_float = ["valeur_fonciere", "longitude","latitude","lot1_surface_carrez"]
df_clean[cols_float] = df_clean[cols_float].apply(pd.to_numeric, errors="coerce")


cols_int = ["nombre_pieces_principales","code_type_local","code_postal"]
df_clean[cols_int] = df_clean[cols_int].apply(pd.to_numeric,errors='coerce').astype('Int64')

df_clean["date_mutation"] = pd.to_datetime(df_clean["date_mutation"], errors="coerce")

df_clean['prix_m_carrez'] = df_clean['valeur_fonciere']/df_clean['lot1_surface_carrez']
df_clean = df_clean.sort_values('date_mutation')

df_clean = df_clean[~df_clean['code_type_local'].isin([1, 3, 4])] #supprime les maisons, les local industriels et les dependances 

print(df_v1.columns)
print(df_v1["nature_culture"].value_counts())
#print(df_clean['code_postal'].value_counts())



df_clean.to_csv('DATA/donnees_immobilieres.csv', index=False, encoding='utf-8')



