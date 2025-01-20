import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")

# Charger les données
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, '..', 'data', 'data_cleaned_outliers.csv')
data = pd.read_csv(file_path)

# Calculer les niveaux différenciés si besoin
data['date_mesure'] = pd.to_datetime(data['date_mesure'])

# Créer le dossier pour enregistrer les visualisations
output_dir = os.path.join(current_dir, '..', 'assets', 'visualizations')
os.makedirs(output_dir, exist_ok=True)

# Liste des piézomètres
piezometres = data['nom_piezo'].unique()

# 1. Répartition des précipitations (RR) par type d'averse
def plot_boxplot_rr(piezometre):
    piezo_data = data[data['nom_piezo'] == piezometre]
    fig = px.box(
        piezo_data, 
        x="type_averse", 
        y="RR", 
        color="type_averse",
        title=f"Répartition des précipitations (RR) par type d'averse\n(Piézomètre : {piezometre})",
        labels={'RR': 'Précipitations (mm)', 'type_averse': 'Type d\'averse'},
        template="plotly_white"
    )
    fig.update_layout(showlegend=False)
    output_file = os.path.join(output_dir, f"boxplot_rr_{normalize_filename(piezometre)}.html")
    fig.write_html(output_file)

# 2. Évolution temporelle des précipitations
def plot_temporal_rr(piezometre):
    piezo_data = data[data['nom_piezo'] == piezometre]
    fig = px.line(
        piezo_data, 
        x="date_mesure", 
        y="RR", 
        title=f"Évolution temporelle des précipitations (RR)\n(Piézomètre : {piezometre})",
        labels={'date_mesure': 'Date de mesure', 'RR': 'Précipitations (mm)'},
        template="plotly_white"
    )
    output_file = os.path.join(output_dir, f"temporal_rr_{normalize_filename(piezometre)}.html")
    fig.write_html(output_file)

# 3. Évolution temporelle des niveaux de nappes
def plot_temporal_niveau(piezometre):
    piezo_data = data[data['nom_piezo'] == piezometre]
    fig = px.line(
        piezo_data, 
        x="date_mesure", 
        y="niveau_nappe_eau", 
        title=f"Évolution temporelle du niveau des nappes\n(Piézomètre : {piezometre})",
        labels={'date_mesure': 'Date de mesure', 'niveau_nappe_eau': 'Niveau des nappes (mètre NGF)'},
        template="plotly_white"
    )
    output_file = os.path.join(output_dir, f"temporal_niveau_{normalize_filename(piezometre)}.html")
    fig.write_html(output_file)

# 4. Diagramme empilé des catégories
def plot_stacked_categories(piezometre):
    piezo_data = data[data['nom_piezo'] == piezometre]
    stacked_counts = pd.crosstab(piezo_data['type_averse'], piezo_data['niveau_categorise'])
    fig = go.Figure()
    for niveau in stacked_counts.columns:
        fig.add_trace(go.Bar(name=niveau, x=stacked_counts.index, y=stacked_counts[niveau]))
    fig.update_layout(
        barmode='stack',
        title=f"Proportion des niveaux par type d'averse\n(Piézomètre : {piezometre})",
        xaxis_title="Type d'averse",
        yaxis_title="Nombre d'observations",
        template="plotly_white"
    )
    output_file = os.path.join(output_dir, f"stacked_categories_{normalize_filename(piezometre)}.html")
    fig.write_html(output_file)

# 5. Matrice de corrélation
def plot_correlation_matrix(piezometre):
    piezo_data = data[data['nom_piezo'] == piezometre]
    correlation_columns = ['niveau_nappe_eau', 'RR', 'TX', 'TN']
    
    # Vérifier si les colonnes nécessaires sont présentes
    if not set(correlation_columns).issubset(piezo_data.columns):
        print(f"Les colonnes nécessaires ne sont pas disponibles pour {piezometre}.")
        return

    # Calculer la matrice de corrélation
    corr_matrix = piezo_data[correlation_columns].corr(method='spearman')

    # Créer la visualisation avec une couleurscale valide
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='viridis',  # Remplacement de 'coolwarm' par 'viridis'
        title=f"Matrice de corrélation (Spearman)\n(Piézomètre : {piezometre})",
        labels={'color': 'Corrélation'}
    )

    # Enregistrer le graphique en HTML
    output_file = os.path.join(output_dir, f"correlation_matrix_{normalize_filename(piezometre)}.html")
    fig.write_html(output_file)

# Générer les graphiques pour chaque piézomètre
for piezometre in piezometres:
    plot_boxplot_rr(piezometre)
    plot_temporal_rr(piezometre)
    plot_temporal_niveau(piezometre)
    plot_stacked_categories(piezometre)
    plot_correlation_matrix(piezometre)

print("Les visualisations ont été générées et sauvegardées dans le dossier './assets/visualizations'.")