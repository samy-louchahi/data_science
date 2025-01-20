import pandas as pd

# Charger les fichiers
chronique_piezo = pd.read_csv('chroniques_piezo.csv')
filtered_stations = pd.read_csv('filtered_stations.csv')
associations = pd.read_csv('piezometres_association_stations.csv')

# Sélectionner les colonnes nécessaires
piezo_cols = ['code_bss', 'date_mesure', 'niveau_nappe_eau', 'profondeur_nappe', 'nom_piezo']
stations_cols = ['station_name', 'DATE', 'RR', 'TX', 'TN','TM',]
association_cols = ['code_bss', 'station_name']

chronique_piezo = chronique_piezo[piezo_cols]
filtered_stations = filtered_stations[stations_cols]
associations = associations[association_cols]

# Harmoniser les formats de date
chronique_piezo['date_mesure'] = pd.to_datetime(chronique_piezo['date_mesure'], format='%Y-%m-%d', errors='coerce')
filtered_stations['DATE'] = pd.to_datetime(filtered_stations['DATE'], format='%Y-%m-%d', errors='coerce')

# Renommer la colonne 'DATE' pour correspondre
filtered_stations = filtered_stations.rename(columns={'DATE': 'date_mesure'})

# Joindre les associations pour s'assurer que chaque piézomètre a la bonne station associée
chronique_piezo = pd.merge(chronique_piezo, associations, on='code_bss', how='inner')

# Vérifier que chaque ligne est associée à la bonne station
combined_data = pd.merge(
    chronique_piezo, 
    filtered_stations, 
    on=['station_name', 'date_mesure'],  # Fusionner sur station_name et date_mesure
    how='inner'
)

# Enregistrer les données combinées
combined_data.to_csv('combined_chroniques.csv', index=False)

print("Données corrigées et enregistrées dans 'combined_chroniques.csv'.")