import pandas as pd

# Charger les données des stations
stations_previous = pd.read_csv('Q_34_previous-1950-2023_RR-T-Vent.csv.gz', compression='gzip', sep=';')
stations_latest = pd.read_csv('Q_34_latest-2024-2025_RR-T-Vent.csv.gz', compression='gzip', sep=';')

# Fusionner les deux jeux de données
stations = pd.concat([stations_previous, stations_latest], ignore_index=True)

# Charger les noms des stations à conserver
piezometres = pd.read_csv('piezometres_association_stations_cleaned.csv')

# Vérifier les valeurs dans AAAAMMJJ avant la conversion
invalid_dates = stations[~stations['AAAAMMJJ'].astype(str).str.isdigit()]  # Filtrer les valeurs non numériques
if not invalid_dates.empty:
    print("Dates invalides détectées :")
    print(invalid_dates)

# Convertir la colonne de date dans stations au format 'AAAA-MM-JJ'
stations['DATE'] = pd.to_datetime(stations['AAAAMMJJ'].astype(str), format='%Y%m%d', errors='coerce')

# Vérifier les dates invalides après conversion
if stations['DATE'].isna().sum() > 0:
    print(f"Nombre de dates invalides : {stations['DATE'].isna().sum()}")
    print(stations[stations['DATE'].isna()])

# Filtrer les données pour retirer les lignes avec des dates invalides
stations = stations.dropna(subset=['DATE'])

# Convertir les colonnes 'date_debut_mesure' et 'date_fin_mesure' dans piezometres au format datetime
piezometres['date_debut_mesure'] = pd.to_datetime(piezometres['date_debut_mesure'], format='%Y-%m-%d', errors='coerce')
piezometres['date_fin_mesure'] = pd.to_datetime(piezometres['date_fin_mesure'], format='%Y-%m-%d', errors='coerce')

# Filtrer les stations par les noms des piézomètres
filtered_stations = stations[stations['NOM_USUEL'].isin(piezometres['station_name'])]

# Joindre les données des piézomètres avec les stations filtrées pour récupérer les dates de mesure
merged_stations = pd.merge(filtered_stations, piezometres[['station_name', 'date_debut_mesure', 'date_fin_mesure']],
                           left_on='NOM_USUEL', right_on='station_name', how='inner')

# Filtrer les données de stations pour ne conserver que celles dont la date de mesure est entre 'date_debut_mesure' et 'date_fin_mesure'
filtered_stations_within_range = merged_stations[
    (merged_stations['DATE'] >= merged_stations['date_debut_mesure']) &
    (merged_stations['DATE'] <= merged_stations['date_fin_mesure'])
]

# Afficher les stations filtrées
print(filtered_stations_within_range)

# Enregistrer les stations filtrées dans un fichier CSV avec le nom "filtered_stations.csv"
filtered_stations_within_range.to_csv('filtered_stations.csv', index=False)

# Message de confirmation
print(f"Les chroniques filtrées ont été enregistrées dans 'filtered_stations.csv'.")