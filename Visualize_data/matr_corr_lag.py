import pandas as pd
import plotly.express as px
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")

# Charger les données nettoyées
current_dir = os.path.dirname(__file__)
file_path_data = os.path.join(current_dir, '..', 'data', 'data_with_lags15.csv')
file_path_lags = os.path.join(current_dir, '..', 'data', 'max_corr_lags.csv')
output_dir = os.path.join(current_dir, '..', 'assets', 'correlation_matrices')

# Charger les fichiers
data = pd.read_csv(file_path_data)
optimal_lags = pd.read_csv(file_path_lags)

# Filtrer les lags ne dépassant pas 15 jours
optimal_lags = optimal_lags[optimal_lags['lag'] <= 15]

# Créer un dossier pour les matrices de corrélation
os.makedirs(output_dir, exist_ok=True)

# Liste des piézomètres
piezometres = optimal_lags['nom_piezo'].unique()

# Générer les matrices de corrélation pour chaque piézomètre
for _, row in optimal_lags.iterrows():
    piezometre = row['nom_piezo']
    lag = int(row['lag'])
    lag_column = f'RR_lag{lag}'  # Nom de la colonne du lag optimal

    # Filtrer les données pour le piézomètre
    piezo_data = data[data['nom_piezo'] == piezometre].dropna(subset=[lag_column, 'niveau_nappe_eau', 'TX', 'TN'])

    if not piezo_data.empty:
        # Sélectionner les colonnes pour la corrélation
        correlation_columns = ['niveau_nappe_eau', lag_column, 'TX', 'TN']
        corr_matrix = piezo_data[correlation_columns].corr(method='spearman')

        # Visualiser avec Plotly
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale='viridis',  # Utiliser une colorscale valide
            title=f"Matrice de corrélation (Lag {lag}) - {piezometre}",
            labels={'color': 'Corrélation'}
        )

        # Sauvegarder chaque matrice au format HTML
        normalized_name = normalize_filename(piezometre)
        file_name = f"correlation_matrix_{normalized_name}_lag{lag}.html"
        fig.write_html(os.path.join(output_dir, file_name))

    else:
        print(f"\nPas de données valides pour {piezometre} avec le lag {lag}")

print(f"Les matrices de corrélation ont été enregistrées dans {output_dir}")