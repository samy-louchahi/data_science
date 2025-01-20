# associer_piezometres_stations.py
import pandas as pd
import math

# Charger les données des stations météo
stations_data = pd.read_csv('stations_meteo.csv')

# Charger les données des piézomètres
piezometres_data = pd.read_csv('selected_piezometres.csv')

# Fonction pour calculer la distance avec la formule Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Rayon de la Terre en km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Fonction pour trouver la station la plus proche pour chaque piézomètre dans un rayon de 10 km
def get_closest_station(piezomètre, stations_df):
    piezo_lat, piezo_lon = piezomètre['y'], piezomètre['x']
    min_distance = float('inf')
    closest_station = None
    
    # Parcourir toutes les stations pour trouver la plus proche dans un rayon de 10 km
    for _, station in stations_df.iterrows():
        station_lat, station_lon = station['Latitude'], station['Longitude']
        distance = haversine(piezo_lat, piezo_lon, station_lat, station_lon)
        
        if distance < min_distance and distance <= 10:
            min_distance = distance
            closest_station = station
    if closest_station is None:
        print(f"Aucune station trouvée pour le piézomètre {piezomètre['code_bss']} {piezomètre['libelle_pe']}dans un rayon de 10 km.")
    
    return closest_station

# Créer une liste vide pour stocker les associations
associations = []

# Appliquer la fonction pour chaque piézomètre et associer les stations
for _, piezo in piezometres_data.iterrows():
    closest_station = get_closest_station(piezo, stations_data)  # Trouver la station la plus proche
    if closest_station is not None:
        associations.append({
            'code_bss': piezo['code_bss'],
            'nom_de_piezometre': piezo['libelle_pe'],  
            'date_debut_mesure': piezo['date_debut_mesure'],
            'date_fin_mesure': piezo['date_fin_mesure'],
            'nb_mesures_piezo': piezo['nb_mesures_piezo'],
            'station_id': closest_station['Id_station'],
            'station_name': closest_station['Nom_usuel'],
            'piézomètre_lat': piezo['y'],
            'piézomètre_lon': piezo['x'],
            'station_lat': closest_station['Latitude'],
            'station_lon': closest_station['Longitude']

        })

# Convertir la liste d'associations en DataFrame
associations_df = pd.DataFrame(associations)

# Sauvegarder le fichier CSV avec les associations
associations_df.to_csv('piezometres_association_stations.csv', index=False)

# Réouvrir le fichier CSV avec les associations
associations_df = pd.read_csv('piezometres_association_stations.csv')

# Fonction pour vérifier la densité des mesures
def has_consistent_measurements(piezometre):
    # Calculer la période totale en jours
    start_date = pd.to_datetime(piezometre['date_debut_mesure'], errors='coerce')
    end_date = pd.to_datetime(piezometre['date_fin_mesure'], errors='coerce')
    
    if pd.isna(start_date) or pd.isna(end_date):
        return False  # Ignorer les lignes avec des dates invalides
    
    total_days = (end_date - start_date).days + 1
    expected_density = piezometre['nb_mesures_piezo'] / total_days  # Densité moyenne
    
    # Vérifier si la densité est raisonnablement proche de 1 (à +/- 20%)
    return 0.8 <= expected_density <= 1.2

# Filtrer les piézomètres avec des mesures cohérentes
consistent_piezometres = associations_df[associations_df.apply(has_consistent_measurements, axis=1)]


print(f"{len(consistent_piezometres)} piézomètres ont des mesures cohérentes.")

# Trouver les trois piézomètres les plus éloignés de leur station associée
associations_df['distance'] = associations_df.apply(
    lambda row: haversine(row['piézomètre_lat'], row['piézomètre_lon'], row['station_lat'], row['station_lon']), axis=1
)

# Trier par distance décroissante et sélectionner les trois premiers
top_3_furthest = associations_df.nlargest(3, 'distance')

# Sauvegarder les trois piézomètres les plus éloignés
top_3_furthest.to_csv('piezometres_association_stations_cleaned.csv', index=False)

print(f"{len(top_3_furthest)} piézomètres avec des mesures cohérentes ont été sauvegardés dans 'piezometres_association_stations_cleaned.csv'.")