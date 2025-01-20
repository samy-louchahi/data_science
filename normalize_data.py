import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Charger les données discrétisées
data = pd.read_csv('data_cleaned_outliers.csv')

# Sélectionner les colonnes numériques à normaliser
columns_to_normalize = ['niveau_nappe_eau', 'RR', 'TX', 'TN']

# MinMaxScaler
minmax_scaler = MinMaxScaler()
data_minmax = data.copy()
data_minmax[columns_to_normalize] = minmax_scaler.fit_transform(data[columns_to_normalize])

# Sauvegarder les données normalisées (MinMaxScaler)
data_minmax.to_csv('data_normalized_minmax.csv', index=False)
print("Données normalisées (MinMaxScaler) sauvegardées dans 'data_normalized_minmax.csv'.")

# Z-score (StandardScaler)
zscore_scaler = StandardScaler()
data_zscore = data.copy()
data_zscore[columns_to_normalize] = zscore_scaler.fit_transform(data[columns_to_normalize])

# Sauvegarder les données normalisées (Z-score)
data_zscore.to_csv('data_normalized_zscore.csv', index=False)
print("Données normalisées (Z-score) sauvegardées dans 'data_normalized_zscore.csv'.")