import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")

# Charger les données nettoyées
data = pd.read_csv('./data/data_cleaned_outliers.csv')

# Créer un dossier pour enregistrer les visualisations
output_dir = './assets/correlation_visualizations'
os.makedirs(output_dir, exist_ok=True)

piezometres = data['nom_piezo'].unique()

# -----------------------------
# Corrélation de Spearman par type d'averse
# -----------------------------
results = []

for piezometre in piezometres:
    piezo_data = data[data['nom_piezo'] == piezometre]

    # Exclure les valeurs de RR égales à 0
    rr_non_zero = piezo_data[piezo_data['RR'] > 0]['RR']

    # Calculer les quantiles uniquement pour les RR > 0
    quantiles = rr_non_zero.quantile([0.25, 0.5, 0.75])

    # Ajuster les seuils pour éviter les duplications
    thresholds = quantiles.unique()
    if len(thresholds) < 3:
        thresholds = np.linspace(rr_non_zero.min(), rr_non_zero.max(), num=4)

    # Créer les bins
    bins = [-np.inf] + list(thresholds) + [np.inf]

    # Reclassification des types d'averses
    piezo_data['type_averse'] = pd.cut(
        piezo_data['RR'],
        bins=bins,
        labels=["légère/nulle", "modérée", "forte", "très forte"],
        duplicates="drop"
    )

    # Calcul des corrélations par type d'averse
    for type_averse in ["légère/nulle", "modérée", "forte", "très forte"]:
        filtered_data = piezo_data[piezo_data['type_averse'] == type_averse]
        
        if len(filtered_data) > 1:
            rr = filtered_data['RR']
            niveau_nappe = filtered_data['niveau_nappe_eau']
            
            # Calculer la corrélation de Spearman
            correlation, p_value = spearmanr(rr, niveau_nappe)
            
            results.append({
                'piezometre': piezometre,
                'type_averse': type_averse,
                'correlation': correlation,
                'p_value': p_value
            })

# Sauvegarder les résultats dans un fichier CSV
results_df = pd.DataFrame(results)
results_file = os.path.join(output_dir, 'correlation_results.csv')
results_df.to_csv(results_file, index=False)
print(f"Les résultats de corrélation ont été sauvegardés dans {results_file}")

# -----------------------------
# Scatterplot par type d'averse
# -----------------------------
scaler = MinMaxScaler()
data['niveau_diff'] = data.groupby('nom_piezo')['niveau_nappe_eau'].diff()
data = data.dropna(subset=['niveau_diff'])
data[['RR_normalized', 'niveau_diff_normalized']] = scaler.fit_transform(data[['RR', 'niveau_diff']])

# Scatterplot pour chaque type d'averse
for piezometre in piezometres:
    piezo_data = data[data['nom_piezo'] == piezometre]
    for type_averse in ["légère/nulle", "modérée", "forte", "très forte"]:
        filtered_data = piezo_data[piezo_data['type_averse'] == type_averse]
        
        if not filtered_data.empty:
            plt.figure(figsize=(10, 6))
            plt.scatter(
                filtered_data['RR_normalized'], 
                filtered_data['niveau_diff_normalized'], 
                alpha=0.5, label=type_averse
            )
            plt.title(f"Relation entre précipitations et variation du niveau des nappes\n(Piézomètre : {piezometre}, Type d'averse : {type_averse})")
            plt.xlabel("Précipitations (RR normalisé)")
            plt.ylabel("Variation du niveau des nappes (normalisé)")
            plt.legend()
            plt.grid()
            
            # Normaliser les noms pour éviter les problèmes
            safe_piezometre = normalize_filename(piezometre)
            safe_type_averse = normalize_filename(type_averse)
            
            scatter_path = os.path.join(output_dir, f"scatter_{safe_piezometre}_{safe_type_averse}.png")
            plt.savefig(scatter_path)
            plt.close()

print(f"Toutes les visualisations ont été sauvegardées dans {output_dir}")