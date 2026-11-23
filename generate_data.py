import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# Pour obtenir les mêmes données à chaque exécution
random.seed(42)

# Créer le dossier data s'il n'existe pas
data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

# 1 - Définir les produits et leurs prix

products = {
    "Laptop": 1200,
    "Phone": 800,
    "Headphones": 150,
    "Tablet": 500,
    "Keyboard": 80
}

#  - Définir les régions où les produits sont vendus
regions = ["Canada", "USA", "France", "Germany"]

#  - Enregistrer les produits dans products.csv
products_data = [
    {"product": name, "price": price}
    for name, price in products.items()
]

pd.DataFrame(products_data).to_csv(
    data_folder / "products.csv", index=False
)

#  - Enregistrer les régions dans regions.csv
pd.DataFrame({"region": regions}).to_csv(
    data_folder / "regions.csv", index=False
)

# 2. Définir la période des ventes
# 

start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 11, 23)

# Calculer le nombre de jours entre les deux dates
total_days = (end_date - start_date).days


# 3. Générer 5000 transactions fictives


sales = []

for i in range(5000):

    # Choisir un produit au hasard
    product = random.choice(list(products.keys()))

    # Choisir une quantité entre 1 et 5
    quantity = random.randint(1, 5)

    # Générer une date aléatoire dans la période
    date = start_date + timedelta(
        days=random.randint(0, total_days)
    )

    # Calculer le revenu de la vente
    revenue = products[product] * quantity

    # Ajouter la transaction à notre liste
    sales.append({
        "order_id": i + 1,
        "date": date.strftime("%Y-%m-%d"),
        "product": product,
        "region": random.choice(regions),
        "quantity": quantity,
        "revenue": revenue
    })


# 4. Introduire volontairement des anomalies


# Anomalie 1 : montant négatif
sales[10]["revenue"] = -500

# Anomalie 2 : région manquante
sales[20]["region"] = None

# Anomalie 3 : transaction dupliquée
sales.append(sales[30].copy())

# Anomalie 4 : quantité incorrecte
sales[40]["quantity"] = -3

# Anomalie 5 : revenu incohérent avec le prix
sales[50]["revenue"] = 99999

# 5. Enregistrer les transactions dans sales.csv


df_sales = pd.DataFrame(sales)

df_sales.to_csv(
    data_folder / "sales.csv",
    index=False
)


# 6. Afficher un résumé dans le terminal

print("Données générées avec succès !")
print(f"Nombre de transactions : {len(df_sales)}")
print(f"Période : {start_date.date()} au {end_date.date()}")
print("Fichiers créés : sales.csv, products.csv, regions.csv")
