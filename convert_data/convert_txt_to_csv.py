import pandas as pd

# Lecture du .txt
df = pd.read_csv("cvf_2025.txt", sep="|", header=None, engine="python")

# Sauvegarde en .csv
df.to_csv("cvf_2025.csv", index=False, encoding="utf-8")
