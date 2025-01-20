import requests
import pandas as pd
from io import StringIO

# Charger les données des piézomètres
piezometres_data = pd.read_csv("piezometres_association_stations_cleaned.csv")
piezometres_bss_id = piezometres_data['code_bss']
nbr_piezo_data = piezometres_data['nb_mesures_piezo']
piezometres_name = piezometres_data['nom_de_piezometre']
print(nbr_piezo_data[0] + nbr_piezo_data[1] + nbr_piezo_data[2])
if nbr_piezo_data[0] + nbr_piezo_data[1] + nbr_piezo_data[2] > 20000:
    nbr_piezo_data = [20000, 0, 0]
# Construire l'URL pour récupérer les chroniques des piézomètres
url = (
    f"https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/chroniques.csv?"
    f"code_bss={piezometres_bss_id[0]},{piezometres_bss_id[1]},{piezometres_bss_id[2]}&"
    f"size={nbr_piezo_data[0] + nbr_piezo_data[1] + nbr_piezo_data[2]}"
)

# Envoyer la requête pour récupérer les chroniques
response = requests.get(url)

# Vérifier si la requête a réussi
if response.status_code in [200, 206]:  # Code 200 (OK) ou 206 (Partial Content)
    # Charger les chroniques dans un DataFrame
    chroniques_piezo = pd.read_csv(StringIO(response.text), delimiter=';')

    # Ajouter une colonne 'nom_piezo' en fonction du 'bss_id'
    # Effectuer une jointure avec piezometres_data
    chroniques_piezo = pd.merge(
        chroniques_piezo,
        piezometres_data[['code_bss', 'nom_de_piezometre']],
        left_on='code_bss',
        right_on='code_bss',
        how='left'
    )

    # Renommer la colonne 'libelle_pe' en 'nom_piezo'
    chroniques_piezo = chroniques_piezo.rename(columns={'nom_de_piezometre': 'nom_piezo'})

    # Sauvegarder les chroniques dans un fichier CSV
    chroniques_piezo.to_csv('chroniques_piezo.csv', index=False)
    print("Les chroniques des piézomètres ont été sauvegardées dans 'chroniques_piezo.csv'.")
else:
    print(f"Erreur lors de la récupération des données des piézomètres: {response.status_code}")