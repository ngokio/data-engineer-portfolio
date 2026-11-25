import pandas as pd
import requests
import re
import os

# 1. LIRE l'Excel sale
df = pd.read_excel("commandes_client.xlsx", dtype=str)
print(f"Au départ : {len(df)} lignes")

# 2. NETTOYER les noms de colonnes
df.columns = [c.strip().lower().replace(" ", "_").replace("€", "").strip("_") for c in df.columns]
print(f"Colonnes nettoyées : {list(df.columns)}")

# 3. ENLEVER les doublons
df = df.drop_duplicates()
print(f"Après doublons : {len(df)} lignes")

# 4. NETTOYER le montant
def clean_montant(x):
    if pd.isna(x) or x == "N/A":
        return 0.0
    s = str(x).replace("€", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

df["montant"] = df["montant"].apply(clean_montant)

# 5. NETTOYER la date
mois_fr = {
    "janvier": "January", "février": "February", "mars": "March",
    "avril": "April", "mai": "May", "juin": "June",
    "juillet": "July", "août": "August", "septembre": "September",
    "octobre": "October", "novembre": "November", "décembre": "December"
}
df["date_commande"] = df["date_commande"].astype(str)
for fr, en in mois_fr.items():
    df["date_commande"] = df["date_commande"].str.replace(fr, en, regex=False)

df["date_commande"] = pd.to_datetime(df["date_commande"], errors="coerce", dayfirst=True, format="mixed")
df = df.dropna(subset=["date_commande"])
print(f"Après dates invalides : {len(df)} lignes")

# 6. NETTOYER l'email et la source
df["email_client"] = df["email_client"].astype(str).str.strip().str.lower()
df["source"] = df["source"].str.strip().str.lower()

# 7. TRANSFORMER en format API
events = []
for _, row in df.iterrows():
    events.append({
        "source": row["source"],
        "event_type": "purchase",
        "user_id": int(row["id_commande"]) if pd.notna(row["id_commande"]) else None,
        "amount": float(row["montant"]),
        "payload": {
            "email": row["email_client"],
            "date_commande": str(row["date_commande"].date()),
            "id_commande_original": int(row["id_commande"])
        }
    })

print(f"Prêt à envoyer : {len(events)} events propres")

# 8. ENVOYER par batch de 500 à ton API
API_URL = os.getenv("API_URL", "http://localhost:8001/ingest/bulk")
API_KEY = os.getenv("API_KEY", "sk-client-12345")
HEADERS = {"x-api-key": API_KEY}

total_inserted = 0
for i in range(0, len(events), 500):
    batch = events[i:i+500]
    r = requests.post(API_URL, json={"events": batch}, headers=HEADERS, timeout=60)
    print(f"Batch {i//500 + 1} : status={r.status_code} body={r.text[:300]}")
    if r.status_code == 200:
        try:
            total_inserted += r.json().get("inserted", 0)
        except:
            print("Erreur JSON, batch ignoré")

print(f"TOTAL inséré : {total_inserted}")