import pandas as pd

# Charger les données avec lags
data = pd.read_csv('combined_chroniques.csv')

# Supprimer les lignes avec des valeurs manquantes
data_cleaned = data.dropna()

# Ajouter une colonne pour classifier les averses
def classify_rainfall(rr):
    if rr == 0:
        return "légère/nulle"
    elif rr <= 10:
        return "légère"
    elif rr <= 30:
        return "modérée"
    elif rr <= 50:
        return "forte"
    else:
        return "très forte"

data_cleaned['type_averse'] = data_cleaned['RR'].apply(classify_rainfall)

# Déterminer les niveaux 'bas', 'moyen', 'haut' pour chaque piézomètre
def classify_niveau(row, quantiles):
    if row['niveau_nappe_eau'] <= quantiles['q33']:
        return "bas"
    elif row['niveau_nappe_eau'] <= quantiles['q66']:
        return "moyen"
    else:
        return "haut"

# Ajouter une colonne 'niveau_categorise' pour chaque piézomètre
niveau_labels = []
for piezometre in data_cleaned['nom_piezo'].unique():
    # Filtrer les données pour le piézomètre en cours
    piezo_data = data_cleaned[data_cleaned['nom_piezo'] == piezometre]
    
    # Calculer les quantiles pour ce piézomètre
    quantiles = {
        'q33': piezo_data['niveau_nappe_eau'].quantile(0.33),
        'q66': piezo_data['niveau_nappe_eau'].quantile(0.66)
    }
    
    # Classifier les niveaux pour ce piézomètre
    for index, row in piezo_data.iterrows():
        niveau_labels.append(classify_niveau(row, quantiles))

# Ajouter les niveaux catégorisés au dataframe nettoyé
data_cleaned['niveau_categorise'] = niveau_labels

# Afficher les informations sur les niveaux
print("Distribution des niveaux par catégorie (bas, moyen, haut) :")
print(data_cleaned['niveau_categorise'].value_counts())

# Enregistrer les données nettoyées
data_cleaned.to_csv('data_cleaned.csv', index=False)
print(f"Données nettoyées et sauvegardées dans 'data_cleaned.csv' avec la classification des averses et niveaux.")