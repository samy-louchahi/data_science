from scipy.signal import correlate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_")

# Charger les données nettoyées
data = pd.read_csv('./data/data_cleaned_outliers.csv')

# Créer un dossier pour enregistrer les graphiques
output_dir = './assets/cross_correlation'
os.makedirs(output_dir, exist_ok=True)

max_corr_lags = {}

for piezometre in data['nom_piezo'].unique():
    piezo_data = data[data['nom_piezo'] == piezometre].dropna(subset=['RR', 'niveau_nappe_eau'])
    
    rr = piezo_data['RR']
    niveau = piezo_data['niveau_nappe_eau']
    
    # Calculer la corrélation croisée
    corr = correlate(niveau, rr, mode='full')
    lags = range(-len(niveau) + 1, len(niveau))
    
    # Trouver le décalage (lag) avec la corrélation maximale
    max_corr_lag = lags[np.argmax(corr)]
    max_corr_lags[piezometre] = max_corr_lag
    print(f"\nPiézomètre : {piezometre}")
    print(f"Décalage (lag) avec corrélation maximale : {max_corr_lag}")
    
    # Enregistrer le graphique de la corrélation croisée
    plt.figure(figsize=(10, 6))
    plt.plot(lags, corr, label="Corrélation croisée")
    plt.axvline(x=max_corr_lag, color='red', linestyle='--', label=f"Lag max ({max_corr_lag} jours)")
    plt.title(f"Corrélation croisée entre RR et niveau d'eau\n(Piézomètre : {piezometre})")
    plt.xlabel("Décalage (jours)")
    plt.ylabel("Corrélation")
    plt.legend()
    plt.grid()

    # Normaliser le nom du fichier
    normalized_piezometre = normalize_filename(piezometre)
    output_file = os.path.join(output_dir, f'cross_correlation_{normalized_piezometre}.png')
    plt.savefig(output_file, dpi=300)
    plt.close()

# Sauvegarder max_corr_lags dans un fichier CSV
max_corr_lags_df = pd.DataFrame(max_corr_lags.items(), columns=['nom_piezo', 'lag'])
max_corr_lags_df.to_csv('./data/max_corr_lags.csv', index=False)
print("Fichier 'max_corr_lags.csv' sauvegardé avec succès.")