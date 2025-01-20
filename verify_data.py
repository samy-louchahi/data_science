import pandas as pd
import numpy as np

# Charger les données nettoyées
data = pd.read_csv('data_cleaned.csv')

# Détection des valeurs aberrantes avec des seuils spécifiques pour `RR`
threshold_std = 3  # Seuil d'écart-type pour les autres colonnes
outliers = {}

# Colonnes à analyser
columns = ['niveau_nappe_eau', 'RR', 'TX', 'TN']

# Définir des seuils spécifiques pour RR
rain_categories = {
    'légère/nulle': (0, 2),
    'modérée': (2, 10),
    'forte': (10, 50),
    'très forte': (50, np.inf)
}

# Traiter chaque colonne
for col in columns:
    if col == 'RR':
        # Vérification pour `RR` en utilisant les seuils des catégories
        outliers[col] = data[(data['RR'] < 0)]  # Par exemple, RR ne doit jamais être négatif
    else:
        # Pour les autres colonnes, détecter les valeurs aberrantes basées sur l'écart-type
        mean = data[col].mean()
        std = data[col].std()
        outliers[col] = data[(data[col] < mean - threshold_std * std) | (data[col] > mean + threshold_std * std)]

    print(f"\nValeurs aberrantes détectées pour {col} :")
    print(outliers[col])

# Supprimer les valeurs aberrantes sauf pour les fortes et très fortes averses dans `RR`
data_cleaned = data.copy()
for col in outliers.keys():
    if col == 'RR':
        # Garder les fortes et très fortes averses
        data_cleaned = data_cleaned[~((data_cleaned.index.isin(outliers[col].index)) & (data_cleaned['RR'] < 10))]
    else:
        # Supprimer les valeurs aberrantes détectées pour les autres colonnes
        data_cleaned = data_cleaned[~data_cleaned.index.isin(outliers[col].index)]

# Sauvegarder les données nettoyées
data_cleaned.to_csv('data_cleaned_outliers.csv', index=False)
print("Données sans valeurs aberrantes sauvegardées dans 'data_cleaned_outliers.csv'.")