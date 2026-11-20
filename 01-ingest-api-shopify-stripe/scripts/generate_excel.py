import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# On fabrique 5000 lignes SALES, comme un vrai client
data = []
for i in range(5000):
    # Montant sale : parfois "1 250,50 €", parfois 1250.5, parfois vide
    montant_sale = random.choice([
        f"{random.randint(10,2000)} €",
        f"{random.randint(10,2000)},50 €",
        f"{random.randint(10,2000)}",
        None,  # vide
        "N/A",
    ])
    # Date sale : 3 formats différents
    date_sale = random.choice([
        (datetime.now() - timedelta(days=random.randint(0,365))).strftime("%d/%m/%Y"),
        (datetime.now() - timedelta(days=random.randint(0,365))).strftime("%Y-%m-%d"),
        "12 mars 2024",
    ])
    # Email sale : majuscules, espaces
    email_sale = random.choice([
        "CLIENT@GMAIL.COM ",
        " jean.dupont@gmail.com",
        None,
        "pas un email",
    ])
    data.append({
        "ID Commande": i+1,
        "Montant €": montant_sale,
        "Date Commande": date_sale,
        "Email Client": email_sale,
        "Source": random.choice(["shopify", "stripe"])
    })

df = pd.DataFrame(data)
# On ajoute 200 doublons exprès
df = pd.concat([df, df.sample(200)], ignore_index=True)
df.to_excel("commandes_client.xlsx", index=False)
print(f"Excel créé : {len(df)} lignes, avec doublons, montants sales, dates sales")