import pandas as pd

# Charger les données nettoyées
data = pd.read_csv('./data/data_cleaned_outliers.csv')

# Liste des piézomètres uniques
piezometres = data['nom_piezo'].unique()

# Initialiser un dictionnaire pour stocker les statistiques descriptives
stats_dict = {}

# Calcul des statistiques descriptives pour chaque piézomètre
for piezometre in piezometres:
    piezo_data = data[data['nom_piezo'] == piezometre]
    
    # Calcul des statistiques descriptives
    stats_dict[piezometre] = {
        'niveau_min': piezo_data['niveau_nappe_eau'].min(),
        'niveau_mean': piezo_data['niveau_nappe_eau'][piezo_data['RR'] > 0].mean(),
        'niveau_max': piezo_data['niveau_nappe_eau'].max(),
        'TX_min': piezo_data['TX'].min(),
        'TX_mean': piezo_data['TX'].mean(),
        'TX_max': piezo_data['TX'].max(),
        'RR_min': piezo_data['RR'].min(),
        'RR_25%': piezo_data['RR'][piezo_data['RR'] > 0].quantile(0.25),
        'RR_50%': piezo_data['RR'][piezo_data['RR'] > 0].quantile(0.50),
        'RR_75%': piezo_data['RR'][piezo_data['RR'] > 0].quantile(0.75),
        'RR_max': piezo_data['RR'].max()
    }

# Convertir le dictionnaire en DataFrame pour affichage
stats_df = pd.DataFrame(stats_dict).transpose()

# Sauvegarder les statistiques dans un fichier CSV
stats_df.reset_index(inplace=True)
stats_df.rename(columns={'index': 'nom_piezo'}, inplace=True)
stats_df.to_csv('./assets/stats_descriptives.csv', index=False)

print("Statistiques descriptives par piézomètre sauvegardées dans './assets/stats_descriptives.csv'.")