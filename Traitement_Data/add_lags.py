import pandas as pd

# Charger les données combinées
data = pd.read_csv('data_normalized_zscore.csv')

# Convertir la colonne de date en datetime si ce n'est pas déjà fait
data['date_mesure'] = pd.to_datetime(data['date_mesure'], format='%Y-%m-%d', errors='coerce')

# Trier les données par date
data = data.sort_values(by='date_mesure')

# Identifier les jours de pluie (RR > 0)
data['is_rainy'] = (data['RR'] > 0).astype(int)

# Ajouter une colonne pour le type d'averse
def classify_averse(rr_value):
    if rr_value == 0:
        return "légère/nulle"
    elif 0 < rr_value <= 5:
        return "modérée"
    elif 5 < rr_value <= 20:
        return "forte"
    else:
        return "très forte"

data['type_averse'] = data['RR'].apply(classify_averse)

# Calculer le cumul des précipitations sur des périodes glissantes
for window in [3, 7, 15]:  # Par exemple, sur des périodes de 3, 7, ou 15 jours
    data[f'RR_cum{window}'] = data['RR'].rolling(window=window, min_periods=1).sum()

# Calculer le nombre de jours consécutifs de pluie dans une fenêtre glissante
for window in [3, 7, 15]:
    data[f'days_with_rain_{window}'] = data['is_rainy'].rolling(window=window, min_periods=1).sum()

# Ajouter des lags pour précipitations et températures (1 à 7 jours)
for lag in range(1, 8):  # Lags de 1 à 7 jours
    data[f'RR_lag{lag}'] = data['RR'].shift(lag)
    data[f'TX_lag{lag}'] = data['TX'].shift(lag)
    data[f'TN_lag{lag}'] = data['TN'].shift(lag)

# Enregistrer les données avec les lags (1 à 7 jours)
data.to_csv('data_with_lags7.csv', index=False)
print("Les lags (1 à 7 jours) ont été ajoutés et sauvegardés dans 'data_with_lags7.csv'.")

# Recharger les données pour les lags de 1 à 15 jours
data = pd.read_csv('data_cleaned.csv')
data['date_mesure'] = pd.to_datetime(data['date_mesure'])
data = data.sort_values(by='date_mesure')

# Identifier les jours de pluie (RR > 0)
data['is_rainy'] = (data['RR'] > 0).astype(int)

# Ajouter une colonne pour le type d'averse
data['type_averse'] = data['RR'].apply(classify_averse)

# Calculer le cumul des précipitations et jours pluvieux
for window in [3, 7, 15]:
    data[f'RR_cum{window}'] = data['RR'].rolling(window=window, min_periods=1).sum()
    data[f'days_with_rain_{window}'] = data['is_rainy'].rolling(window=window, min_periods=1).sum()

# Ajouter des lags pour précipitations et températures (1 à 15 jours)
for lag in range(1, 16):  # Lags de 1 à 15 jours
    data[f'RR_lag{lag}'] = data['RR'].shift(lag)
    data[f'TX_lag{lag}'] = data['TX'].shift(lag)
    data[f'TN_lag{lag}'] = data['TN'].shift(lag)

# Enregistrer les données avec les lags (1 à 15 jours)
data.to_csv('data_with_lags15.csv', index=False)
print("Les lags (1 à 15 jours) ont été ajoutés et sauvegardés dans 'data_with_lags15.csv'.")