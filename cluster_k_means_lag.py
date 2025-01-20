from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import matplotlib.pyplot as plt
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_")

# Dossier pour enregistrer les graphiques
ASSETS_DIR = './assets/clustering_lags'

# Créer le dossier s'il n'existe pas
os.makedirs(ASSETS_DIR, exist_ok=True)

# Charger les données nettoyées avec les lags
data = pd.read_csv('./data/data_with_lags15.csv')

# Charger les lags optimaux par piézomètre
optimal_lags = pd.read_csv('./assets/max_corr_lags.csv')  # Fichier contenant 'nom_piezo' et 'lag'

# Initialiser le scaler pour normalisation
scaler = MinMaxScaler()

# Itérer sur les piézomètres et leurs lags optimaux
for _, row in optimal_lags.iterrows():
    piezometre = row['nom_piezo']
    lag = int(row['lag'])
    lag_column = f'RR_lag{lag}'  # Construire dynamiquement le nom de la colonne

    # Ignorer les lags supérieurs à 15 ou les colonnes inexistantes
    if lag > 15 or lag_column not in data.columns:
        continue

    # Filtrer les données pour le piézomètre et les colonnes nécessaires
    piezo_data = data[data['nom_piezo'] == piezometre].dropna(subset=[lag_column, 'niveau_nappe_eau'])

    if not piezo_data.empty:
        # Préparer les données pour le clustering
        X = scaler.fit_transform(piezo_data[[lag_column, 'niveau_nappe_eau']])

        # Effectuer le clustering KMeans
        kmeans = KMeans(n_clusters=3, random_state=42)
        piezo_data['cluster'] = kmeans.fit_predict(X)

        # Visualisation des clusters
        plt.figure(figsize=(10, 6))
        plt.scatter(
            piezo_data[lag_column], piezo_data['niveau_nappe_eau'], 
            c=piezo_data['cluster'], cmap='viridis', alpha=0.6
        )
        plt.title(f"Clustering pour {piezometre} (Lag {lag})")
        plt.xlabel(f"Précipitations décalées (RR_lag{lag})")
        plt.ylabel("Niveau des nappes (mètre NGF)")
        plt.colorbar(label="Cluster")
        plt.grid()

        # Ajouter le centre des clusters au graphique
        cluster_centers = kmeans.cluster_centers_
        cluster_centers_unnormalized = scaler.inverse_transform(cluster_centers)
        for center in cluster_centers_unnormalized:
            plt.scatter(center[0], center[1], c='red', marker='x', s=100, label="Centroid")
        
        plt.legend()

        # Normaliser le nom du fichier
        normalized_piezometre = normalize_filename(piezometre)
        output_file = f"{ASSETS_DIR}/clustering_{normalized_piezometre}_lag{lag}.png"

        # Enregistrer le graphique
        plt.savefig(output_file)
        plt.close()

        # Calculer et afficher les statistiques descriptives pour chaque cluster
        stats = piezo_data.groupby('cluster')[[lag_column, 'niveau_nappe_eau']].mean()
        print(f"\nStatistiques descriptives pour le piézomètre {piezometre} (Lag {lag}):")
        print(stats)
    else:
        print(f"\nPiézomètre : {piezometre}")
        print(f"Lag optimal : {lag}")
        print("Aucune donnée disponible après filtrage.")