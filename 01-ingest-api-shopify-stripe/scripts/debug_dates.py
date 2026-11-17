import pandas as pd

df = pd.read_excel("commandes_client.xlsx", dtype=str)
print("Colonnes BRUTES dans l'Excel :", list(df.columns))

# On nettoie les noms comme dans ingest_excel.py
df.columns = [c.strip().lower().replace(" ", "_").replace("€", "").strip("_") for c in df.columns]
print("Colonnes NETTOYÉES :", list(df.columns))

print("\nType de la colonne :", df["date_commande"].dtype)
print("\n--- 20 premières valeurs BRUTES ---")
print(df["date_commande"].head(20).to_list())
print("\n--- Valeurs uniques ---")
print(df["date_commande"].unique()[:10])