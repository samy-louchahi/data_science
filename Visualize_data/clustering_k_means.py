import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
from kneed import KneeLocator
import os

# Charger les données
data = pd.read_csv('./data/data_normalized_minmax.csv')

# Calculer la variation du niveau d'eau pour chaque piézomètre
data['niveau_diff'] = data.groupby('nom_piezo')['niveau_nappe_eau'].diff()

# Supprimer les NaN (causés par le calcul des variations)
data = data.dropna(subset=['niveau_diff'])

# Normaliser les colonnes nécessaires pour le clustering
scaler = MinMaxScaler()
data[['RR_normalized', 'niveau_diff_normalized']] = scaler.fit_transform(data[['RR', 'niveau_diff']])

# Obtenir la liste des piézomètres uniques
piezometres = data['nom_piezo'].unique()

# Créer le dossier 'assets' s'il n'existe pas déjà
output_dir = './assets'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Tracer un clustering K-Means pour chaque piézomètre avec détermination du nombre optimal de clusters
for piezometre in piezometres:
    # Filtrer les données pour le piézomètre en cours
    piezo_data = data[data['nom_piezo'] == piezometre]
    
    # Variables pour le clustering
    X = piezo_data[['RR_normalized', 'niveau_diff_normalized']]
    
    # Déterminer le nombre optimal de clusters avec la méthode du coude
    inertia = []
    k_range = range(1, 10)  # Tester de 1 à 10 clusters
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X)
        inertia.append(kmeans.inertia_)
    
    # Trouver le "coude"
    knee = KneeLocator(k_range, inertia, curve="convex", direction="decreasing")
    optimal_k = knee.knee
    print(f"Nombre optimal de clusters pour le piézomètre {piezometre} : {optimal_k}")
    
    # Tracer la courbe du coude et enregistrer en PNG
    plt.figure(figsize=(8, 6))
    plt.plot(k_range, inertia, marker='o')
    plt.axvline(optimal_k, color='r', linestyle='--', label=f"Optimal k = {optimal_k}")
    plt.title(f"Méthode du coude pour {piezometre}")
    plt.xlabel("Nombre de clusters")
    plt.ylabel("Inertie (somme des distances)")
    plt.legend()
    plt.grid()
    elbow_plot_path = os.path.join(output_dir, f'elbow_plot_{piezometre}.png')
    plt.savefig(elbow_plot_path)
    print(f"Courbe du coude sauvegardée : {elbow_plot_path}")
    plt.close()
    
    # Appliquer K-Means avec le nombre optimal de clusters
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    piezo_data['cluster'] = kmeans.fit_predict(X)
    
    # Centroides des clusters
    centroids = kmeans.cluster_centers_
    
    # Créer le scatterplot pour le piézomètre en cours et enregistrer en PNG
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=piezo_data['RR_normalized'], 
        y=piezo_data['niveau_diff_normalized'], 
        hue=piezo_data['cluster'], 
        palette='viridis', 
        alpha=0.7
    )
    plt.scatter(
        centroids[:, 0], 
        centroids[:, 1], 
        c='red', 
        s=200, 
        label='Centroids', 
        marker='X'
    )
    plt.title(f"Clustering des précipitations et variations de niveau d'eau pour le piézomètre : {piezometre}")
    plt.xlabel("Précipitations (RR normalisé)")
    plt.ylabel("Variation du niveau des nappes (normalisé)")
    plt.legend(title="Cluster")
    plt.grid()
    scatter_plot_path = os.path.join(output_dir, f'cluster_plot_{piezometre}.png')
    plt.savefig(scatter_plot_path)
    print(f"Scatterplot sauvegardé : {scatter_plot_path}")
    plt.close()
    
    # Afficher les statistiques descriptives pour chaque cluster
    print(f"\nStatistiques descriptives pour le piézomètre {piezometre} :")
    print(piezo_data.groupby('cluster')[['RR', 'niveau_diff']].mean())