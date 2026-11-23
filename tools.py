# AI BUSINESS ANALYST - TOOLS
# tools.py contient les outils d'analyse de données.

# Notre agent IA pourra utiliser ces fonctions pour :
# 1. Explorer les fichiers CSV
# 2. Analyser les ventes
# 3. Comparer deux années
# 4. Détecter les anomalies dans les données
# 5. Générer des graphiques
# 
# Notes:  
#   Les calculs sont réalisés par Pandas.
#   Qwen choisit les outils, mais n'invente pas les résultats.
# 


from pathlib import Path
import json
import calendar

import pandas as pd

# Nous utilisons Agg pour générer des graphiques
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt



# 1 -  CONFIGURATION DES DOSSIERS

BASE_DIR = Path(__file__).resolve().parent

# Dossier contenant nos données commerciales.
DATA_DIR = BASE_DIR / "data"

# Dossier où seront enregistrés les graphiques et rapports.
REPORT_DIR = BASE_DIR / "reports"


# 2 - CHARGEMENT DES DONNÉES

def load_sales():
    """
    Charger le fichier sales.csv.
    - lit les transactions avec Pandas ;
    - convertit la colonne date au format datetime ;
    - retourne un DataFrame.
    """

    file_path = DATA_DIR / "sales.csv"

    # Lire le fichier CSV.
    df = pd.read_csv(file_path)

    # Convertir les dates pour permettre les filtres
    # par année, mois ou période.
    # Une date invalide devient NaT (date manquante).
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    return df


# 4. EXPLORATION DES DONNÉES

def explore_data():
    """
    Explorer automatiquement les fichiers CSV.

    L'agent pourra découvrir :
    - les fichiers disponibles ;
    - le nombre de lignes ;
    - les colonnes ;
    - quelques exemples de données.

    Utile lorsqu'il ne connaît pas
    encore la structure des données.
    """

    result = {}

    # Parcourir tous les fichiers CSV du dossier data.
    for file_path in sorted(DATA_DIR.glob("*.csv")):

        # Charger le fichier courant.
        df = pd.read_csv(file_path)

        # Enregistrer ses informations principales.
        result[file_path.name] = {
            "rows": len(df),
            "columns": list(df.columns),
            "sample": df.head(3).to_dict(
                orient="records"
            )
        }

    # Transformer le dictionnaire Python en JSON.
    # Le JSON est facile à interpréter pour Qwen.
    return json.dumps(
        result,
        ensure_ascii=False,
        default=str
    )


# 5. ANALYSE DES VENTES

def analyze_sales(year=None, group_by="region"):
    """
    Calculer les revenus commerciaux.

    Cette fonction calcule :
    - le revenu total par groupe ;
    - le nombre de transactions par groupe.
    """

    # Limiter les regroupements aux colonnes autorisées.
    allowed_groups = ["year", "region", "product"]

    if group_by not in allowed_groups:
        return (
            "Erreur : group_by doit être "
            "year, region ou product."
        )

    # Charger les ventes.
    df = load_sales()

    # Si une année est fournie, filtrer les transactions.
    if year is not None:
        year = int(year)

        df = df[
            df["date"].dt.year == year
        ]

    # Vérifier que des transactions existent.
    if df.empty:
        return "Aucune transaction trouvée."

    # La colonne year n'existe pas dans sales.csv.
    # Nous la créons à partir de la colonne date.
    if group_by == "year":
        df = df.copy()

        df["year"] = df["date"].dt.year

    # Regrouper les transactions.
    # sum = revenu total
    # count = nombre de transactions
    result = (
        df.groupby(
            group_by,
            dropna=False
        )["revenue"]
        .agg(["sum", "count"])
        .reset_index()
    )

    # Renommer les colonnes pour faciliter la lecture.
    result = result.rename(
        columns={
            "sum": "total_revenue",
            "count": "transactions"
        }
    )

    # Retourner les résultats au format JSON.
    return result.to_json(
        orient="records",
        force_ascii=False
    )


# 6. COMPARAISON DE DEUX ANNÉES

def compare_years(year1, year2):
    """
    Comparer les revenus de deux années.

    """
    year1 = int(year1)
    year2 = int(year2)

    # Charger les ventes et retirer les dates invalides.
    df = load_sales().dropna(subset=["date"])

    # Séparer les deux années.
    sales1 = df[
        df["date"].dt.year == year1
    ].copy()

    sales2 = df[
        df["date"].dt.year == year2
    ].copy()

    # Impossible de comparer une année sans données.
    if sales1.empty or sales2.empty:
        return (
            "Erreur : données insuffisantes "
            "pour comparer ces deux années."
        )

    # Déterminer la dernière date disponible dans chacune des années.
    last_date1 = sales1["date"].max()
    last_date2 = sales2["date"].max()

    # Retenir le mois et le jour les plus précoces.
    cutoff_month_day = min(
        (last_date1.month, last_date1.day),
        (last_date2.month, last_date2.day)
    )

    # Adapter le jour si nécessaire pour une année non bissextile.
    def cutoff_for_year(year):
        month, day = cutoff_month_day

        max_day = calendar.monthrange(year, month)[1]

        return pd.Timestamp(
            year=year,
            month=month,
            day=min(day, max_day)
        )

    cutoff1 = cutoff_for_year(year1)
    cutoff2 = cutoff_for_year(year2)

    # Garder uniquement les transactions jusqu'à la date comparable.
    sales1 = sales1[
        sales1["date"] <= cutoff1
    ]

    sales2 = sales2[
        sales2["date"] <= cutoff2
    ]

    # Calculer les revenus.
    revenue1 = float(sales1["revenue"].sum())
    revenue2 = float(sales2["revenue"].sum())

    # Calculer la différence absolue.
    difference = revenue2 - revenue1

    # Calculer le pourcentage d'évolution.
    # Éviter une division par zéro.
    if revenue1 != 0:
        change_percent = (
            difference / revenue1
        ) * 100
    else:
        change_percent = None

    # Préparer le résultat.
    result = {
        "year1": year1,
        "year2": year2,
        "period1": (
            f"{year1}-01-01 au "
            f"{cutoff1.date()}"
        ),
        "period2": (
            f"{year2}-01-01 au "
            f"{cutoff2.date()}"
        ),
        "revenue1": round(revenue1, 2),
        "revenue2": round(revenue2, 2),
        "difference": round(difference, 2),
        "change_percent": (
            round(change_percent, 2)
            if change_percent is not None
            else None
        )
    }

    return json.dumps(
        result,
        ensure_ascii=False
    )


# 7. CONTRÔLE DE QUALITÉ DES DONNÉES

def check_data_quality():
    """
    Détecter les problèmes dans les données.
    - les identifiants de commande dupliqués ;
    - les valeurs manquantes ;
    - les quantités négatives ;
    - les revenus négatifs ;
    - les revenus incohérents ;
    - les produits inconnus.
    """

    # Charger les transactions.
    df = load_sales()

    # Charger le catalogue des produits.
    products = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    # Associer le prix officiel à chaque transaction.
    merged = df.merge(
        products,
        on="product",
        how="left",
        validate="many_to_one"
    )

    # Calculer le revenu théorique.
    expected_revenue = (
        merged["price"] * merged["quantity"]
    )

    # Détecter les revenus différents du montant attendu.
    mismatches = (
        merged["revenue"].notna()
        & expected_revenue.notna()
        & (
            abs(
                merged["revenue"] - expected_revenue
            ) > 0.01
        )
    )

    # Détecter les valeurs négatives.
    negative_quantities = merged["quantity"] < 0
    negative_revenues = merged["revenue"] < 0

    # Détecter les produits sans prix dans le catalogue.
    unknown_products = merged["price"].isna()

    # Détecter les commandes ayant le même identifiant.
    duplicate_ids = df["order_id"].duplicated(
        keep=False
    )

    # Regrouper les transactions suspectes.
    suspicious = (
        mismatches
        | negative_quantities
        | negative_revenues
        | unknown_products
    )

    result = {
        "total_transactions": len(df),

        "duplicate_order_ids": int(
            df["order_id"].duplicated().sum()
        ),

        "duplicate_examples": df.loc[
            duplicate_ids,
            "order_id"
        ].head(10).tolist(),

        "missing_values": {
            column: int(count)
            for column, count
            in df.isna().sum().items()
            if count > 0
        },

        "negative_quantities": int(
            negative_quantities.sum()
        ),

        "negative_revenues": int(
            negative_revenues.sum()
        ),

        "revenue_mismatches": int(
            mismatches.sum()
        ),

        "unknown_products": int(
            unknown_products.sum()
        ),

        "suspicious_order_examples": merged.loc[
            suspicious,
            "order_id"
        ].head(20).tolist()
    }

    return json.dumps(
        result,
        ensure_ascii=False,
        default=str
    )


# 8. GÉNÉRATION AUTOMATIQUE DES GRAPHIQUES

def create_chart(group_by="year", year=None):
    """
    Créer un graphique des revenus avec Matplotlib.
    """

    allowed_groups = ["year", "region", "product"]

    if group_by not in allowed_groups:
        return "Erreur : regroupement non autorisé."

    # Charger les données.
    df = load_sales()

    # Filtrer par année si demandé.
    if year is not None:
        year = int(year)

        df = df[
            df["date"].dt.year == year
        ]

    if df.empty:
        return "Aucune donnée pour créer le graphique."

    # Créer une colonne year si nécessaire.
    if group_by == "year":
        df = df.copy()

        df["year"] = df["date"].dt.year

    # Calculer les revenus par catégorie.
    values = (
        df.groupby(
            group_by,
            dropna=False
        )["revenue"]
        .sum()
        .sort_index()
    )

    # Convertir les catégories en texte
    # pour gérer aussi les valeurs manquantes.
    labels = values.index.map(str)

    # Créer le dossier reports s'il n'existe pas.
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Construire un nom de fichier descriptif.
    suffix = (
        f"_{year}"
        if year is not None
        else ""
    )

    filename = (
        f"revenue_by_{group_by}{suffix}.png"
    )

    output_path = REPORT_DIR / filename

    # Créer la figure.
    fig, ax = plt.subplots(
        figsize=(9, 5)
    )

    # Dessiner les barres.
    ax.bar(
        labels,
        values.to_numpy()
    )

    # Ajouter un titre et les noms des axes.
    ax.set_title(
        f"Revenue by {group_by}{suffix}"
    )

    ax.set_xlabel(group_by.capitalize())
    ax.set_ylabel("Revenue (synthetic units)")

    # Améliorer la disposition du graphique.
    plt.xticks(rotation=30)
    fig.tight_layout()

    # Enregistrer l'image sur le disque.
    fig.savefig(
        output_path,
        dpi=150
    )

    # Libérer la mémoire.
    plt.close(fig)

    return json.dumps({
        "status": "success",
        "file": filename,
        "path": str(output_path)
    }, ensure_ascii=False)


# 9. REGISTRE DES OUTILS

# Ce dictionnaire associe le nom de chaque outil
# à sa fonction Python.
# Exemple :
# Si Qwen choisit "check_data_quality",
# agent.py exécutera la fonction correspondante.

TOOLS = {
    "explore_data": explore_data,
    "analyze_sales": analyze_sales,
    "compare_years": compare_years,
    "check_data_quality": check_data_quality,
    "create_chart": create_chart
}
