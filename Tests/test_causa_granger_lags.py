from statsmodels.tsa.stattools import grangercausalitytests
import pandas as pd
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")

# Charger les données nettoyées
data = pd.read_csv('./data/data_with_lags15.csv')

# Charger les lags optimaux par piézomètre
optimal_lags = pd.read_csv('./assets/max_corr_lags.csv')  # Fichier contenant les colonnes 'nom_piezo' et 'lag'

# Créer un dictionnaire pour stocker les résultats
results = []

# Itérer sur les piézomètres et leurs lags optimaux
for _, row in optimal_lags.iterrows():
    piezometre = row['nom_piezo']
    lag = int(row['lag'])  # S'assurer que le lag est un entier
    lag_column = f'RR_lag{lag}'  # Construire dynamiquement le nom de la colonne

    if lag > 15:
        print(f"\nPiézomètre : {piezometre}")
        print(f"Lag optimal : {lag} -> Ignoré car supérieur à 15.")
        continue
    
    # Filtrer les données pour le piézomètre et les colonnes nécessaires
    piezo_data = data[data['nom_piezo'] == piezometre].dropna(subset=[lag_column, 'niveau_nappe_eau'])
    
    if not piezo_data.empty:
        # Préparer les données pour le test de causalité
        lags_data = piezo_data[['niveau_nappe_eau', lag_column]]

        # Effectuer le test de causalité de Granger
        print(f"\nPiézomètre : {piezometre}")
        test_result = grangercausalitytests(lags_data, maxlag=lag, verbose=False)

        # Enregistrer les résultats pour chaque lag
        for lag_key, result in test_result.items():
            p_value = result[0]['ssr_ftest'][1]  # P-value du test F
            results.append({
                'piezometre': normalize_filename(piezometre),
                'lag_tested': lag_key,
                'optimal_lag': lag,
                'p_value': p_value
            })
    else:
        print(f"\nPiézomètre : {piezometre}")
        print(f"Lag optimal : {lag}")
        print("Aucune donnée disponible après filtrage.")

# Convertir les résultats en DataFrame
results_df = pd.DataFrame(results)

# Créer un dossier pour enregistrer les résultats
output_dir = './assets'
os.makedirs(output_dir, exist_ok=True)

# Sauvegarder les résultats dans un fichier CSV
results_file_path = os.path.join(output_dir, 'granger_results.csv')
results_df.rename(columns={'piezometre': 'nom_piezo'}, inplace=True)
results_df.to_csv('./assets/granger_results.csv', index=False)

print(f"Les résultats des tests de causalité de Granger ont été sauvegardés dans '{results_file_path}'.")