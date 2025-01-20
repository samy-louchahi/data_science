import requests
import pandas as pd
from io import StringIO

# Définir la BBOX pour l'Hérault
bbox = "3.1,43.3,4.5,44.5"  # Coordonnées approximatives de l'Hérault
url = f"https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/stations.csv?bbox={bbox}"

# Envoyer la requête pour récupérer les stations
response = requests.get(url)

if response.status_code == 200:
    # Charger les données dans un DataFrame
    stations_data = pd.read_csv(StringIO(response.text), delimiter=';')

    # Convertir les colonnes de dates en datetime
    stations_data['date_debut_mesure'] = pd.to_datetime(stations_data['date_debut_mesure'], errors='coerce')
    stations_data['date_fin_mesure'] = pd.to_datetime(stations_data['date_fin_mesure'], errors='coerce')

    # Convertir la colonne `date_maj` avec le bon format
    stations_data['date_maj'] = pd.to_datetime(stations_data['date_maj'], format='%a %b %d %H:%M:%S %Z %Y', errors='coerce')

    # Filtrer les stations pour le département Hérault et exclure les valeurs manquantes
    stations_data = stations_data[
        (stations_data['nom_departement'] == 'Hérault') &
        (stations_data['noms_masse_eau_edl'].notna()) &
        (stations_data['noms_masse_eau_edl'] != '')
    ]

    # Étape 1 : Fiabilité des données (date_maj)
    # Garder uniquement les stations avec une mise à jour récente
    stations_data = stations_data.sort_values(by='date_maj', ascending=False)

    # Étape 2 : Données longues et régulières
    # Calculer l'intervalle de mesures
    stations_data['interval_mesures'] = (stations_data['date_fin_mesure'] - stations_data['date_debut_mesure']).dt.days

    # Trier par intervalle de mesures et par nombre de mesures
    stations_data = stations_data.sort_values(by=['interval_mesures', 'nb_mesures_piezo'], ascending=[False, False])

    # Étape 3 : Diversité géographique
    # Garder les stations ayant des masses d'eau distinctes (noms_masse_eau_edl)
    selected_piezometres = stations_data.drop_duplicates(subset=['noms_masse_eau_edl'])

    # Limiter à 3 stations avec les critères prioritaires (fiabilité, longueur des données, diversité géographique)
   # selected_piezometres = selected_piezometres.head(3)

    # Supprimer les colonnes inutiles
    columns_to_keep = [
        'code_bss', 'nom_departement','libelle_pe', 'nom_commune','x','y', 'noms_masse_eau_edl', 
        'nb_mesures_piezo', 'date_debut_mesure', 'date_fin_mesure', 'date_maj'
    ]
    selected_piezometres = selected_piezometres[columns_to_keep]

    # Enregistrer les piézomètres sélectionnés dans un fichier CSV
    selected_piezometres.to_csv('selected_piezometres.csv', index=False)

    # Afficher un message de confirmation
    print("Les 3 piézomètres sélectionnés ont été enregistrés dans 'selected_piezometres.csv'.")
else:
    print("Erreur lors de la récupération des données :", response.status_code)