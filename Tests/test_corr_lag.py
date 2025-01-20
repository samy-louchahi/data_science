import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")

# Charger les données nettoyées
data = pd.read_csv('./data/data_with_lags15.csv')

# Charger les lags optimaux par piézomètre
optimal_lags = pd.read_csv('./assets/max_corr_lags.csv')  # Fichier contenant les colonnes 'nom_piezo' et 'lag'

# Créer un répertoire pour enregistrer les visualisations
output_dir = './assets/corr_lag_visualizations'
os.makedirs(output_dir, exist_ok=True)

# Itérer sur les piézomètres et leurs lags optimaux
for _, row in optimal_lags.iterrows():
    piezometre = row['nom_piezo']
    lag = int(row['lag'])  # S'assurer que le lag est un entier

    if lag > 15:
        print(f"\nPiézomètre : {piezometre}")
        print(f"Lag optimal : {lag} -> Ignoré car supérieur à 15.")
        continue

    lag_column = f'RR_lag{lag}'  # Construire dynamiquement le nom de la colonne

    # Vérifier si la colonne existe
    if lag_column not in data.columns:
        print(f"\nPiézomètre : {piezometre}")
        print(f"Lag optimal : {lag} -> Colonne {lag_column} absente dans les données.")
        continue

    # Filtrer les données pour le piézomètre et les colonnes nécessaires
    piezo_data = data[data['nom_piezo'] == piezometre].dropna(subset=[lag_column, 'niveau_nappe_eau'])

    if not piezo_data.empty:
        # Extraire les données pertinentes
        rr_lag = piezo_data[lag_column]
        niveau = piezo_data['niveau_nappe_eau']

        # Calculer la corrélation de Spearman pour le lag optimal
        correlation, p_value = spearmanr(rr_lag, niveau)

        # Scatterplot avec annotations
        plt.figure(figsize=(10, 6))
        plt.scatter(rr_lag, niveau, alpha=0.6, label=f"Lag {lag}")
        plt.title(f"Relation entre précipitations décalées et niveau des nappes\n(Piézomètre : {piezometre})")
        plt.xlabel(f"Précipitations décalées (RR_lag{lag})")
        plt.ylabel("Niveau des nappes (mètre NGF)")
        plt.legend()
        plt.grid()
        text = (f"Corrélation : {correlation:.4f}\nP-value : {p_value:.4f}\nLag optimal : {lag}")
        plt.gca().text(0.95, 0.05, text, fontsize=10, transform=plt.gca().transAxes,
                       verticalalignment='bottom', horizontalalignment='right',
                       bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        scatter_path = os.path.join(output_dir, f"scatter_{normalize_filename(piezometre)}_lag{lag}.png")
        plt.savefig(scatter_path)
        plt.close()

        # Courbes temporelles avec annotations
        piezo_data = piezo_data.sort_values(by='date_mesure')  # Assurer l'ordre chronologique
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(piezo_data['date_mesure'], niveau, label='Niveau des nappes', color='blue')
        ax1.set_ylabel('Niveau des nappes (mètre NGF)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax2 = ax1.twinx()
        ax2.plot(piezo_data['date_mesure'], rr_lag, label=f'RR_lag{lag}', color='orange')
        ax2.set_ylabel('Précipitations (mm)', color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')
        text = (f"Corrélation : {correlation:.4f}\nP-value : {p_value:.4f}\nLag optimal : {lag}")
        plt.gca().text(0.95, 0.95, text, fontsize=10, transform=plt.gca().transAxes,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        plt.title(f"Évolution temporelle des précipitations décalées et niveau des nappes\n(Piézomètre : {piezometre})")
        fig.tight_layout()
        plt.grid()
        temporal_path = os.path.join(output_dir, f"temporal_{normalize_filename(piezometre)}_lag{lag}.png")
        plt.savefig(temporal_path)
        plt.close()
    else:
        print(f"\nPiézomètre : {piezometre}")
        print(f"Lag optimal : {lag}")
        print("Aucune donnée disponible après filtrage.")