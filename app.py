import dash
from dash import dcc, html, Input, Output, dash_table
import os
import pandas as pd

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")

# Créer l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server


# Dossiers contenant les graphiques
ASSETS_CLUSTER = 'assets/clustering'
ASSETS_CLUSTER_LAGS = 'assets/clustering_lags'
ASSETS_CROSS_CORR = 'assets/cross_correlation'
ASSETS_GENE_VISUAL = './assets/visualizations'
ASSETS_CORR_MATRICES = 'assets/correlation_matrices'

# Charger les graphiques pour clustering_k_means.py
def load_clustering_graphs():
    files = os.listdir(ASSETS_CLUSTER)
    return [f"/{ASSETS_CLUSTER}/{file}" for file in files if file.endswith('.png')]

# Charger les graphiques pour cluster_k_means_lags.py
def load_clustering_lags_graphs():
    files = os.listdir(ASSETS_CLUSTER_LAGS)
    graph_data = {}
    for file in files:
        if file.endswith('.png'):
            parts = file.replace('clustering_', '').replace('.png', '').split('_lag')
            piezometre, lag = parts[0], parts[1]
            piezometre = normalize_filename(piezometre)  # Normaliser le nom du piézomètre
            if piezometre not in graph_data:
                graph_data[piezometre] = []
            graph_data[piezometre].append({'lag': lag, 'path': f"/{ASSETS_CLUSTER_LAGS}/{file}"})
    return graph_data

# Charger les graphiques pour corrélation croisée
def load_cross_corr_graphs():
    files = os.listdir(ASSETS_CROSS_CORR)
    return [f"/{ASSETS_CROSS_CORR}/{file}" for file in files if file.endswith('.png')]

# Charger les graphiques pour gene_data_visual.py
def load_gene_visual_graphs():
    files = os.listdir(ASSETS_GENE_VISUAL)
    graph_data = {}
    for file in files:
        if file.endswith('.html') or file.endswith('.png'):
            # Extraire et normaliser le nom du piézomètre
            piezometre = file.replace('boxplot_rr_', '').replace('temporal_rr_', '').replace('temporal_niveau_', '') \
                            .replace('stacked_categories_', '').replace('correlation_matrix_', '').replace('.html', '').replace('.png', '')
            piezometre = normalize_filename(piezometre)

            # Ajouter les fichiers au dictionnaire
            if piezometre not in graph_data:
                graph_data[piezometre] = []
            graph_data[piezometre].append(f"/{ASSETS_GENE_VISUAL}/{file}")
    return graph_data

# Charger les matrices de corrélation (HTML)
def load_corr_matrices():
    files = os.listdir(ASSETS_CORR_MATRICES)
    return [f"{ASSETS_CORR_MATRICES}/{file}" for file in files if file.endswith('.html')]

# Charger les graphiques
clustering_graphs = load_clustering_graphs()
clustering_lags_graphs = load_clustering_lags_graphs()
cross_corr_graphs = load_cross_corr_graphs()
gene_visual_graphs = load_gene_visual_graphs()
corr_matrices_graphs = load_corr_matrices()
piezometres_gene_visual = list(gene_visual_graphs.keys())
piezometres_lags = list(clustering_lags_graphs.keys())

# Charger les données supplémentaires
stats_file_path = './assets/stats_descriptives.csv'
stats_data = pd.read_csv(stats_file_path)
granger_results_file_path = './assets/granger_results.csv'
granger_results = pd.read_csv(granger_results_file_path)
chi2_results_file_path = './assets/chi2_results.csv'
chi2_results = pd.read_csv(chi2_results_file_path)
chi2_visualizations_dir = './assets/chi2_visualizations'
chi2_visualizations = [
    os.path.join(chi2_visualizations_dir, file)
    for file in os.listdir(chi2_visualizations_dir) if file.endswith('.png')
]
corr_lag_dir = './assets/corr_lag_visualizations'
corr_lag_visualizations = [
    os.path.join(corr_lag_dir, file)
    for file in os.listdir(corr_lag_dir) if file.endswith('.png')
]
corr_visualizations_dir = './assets/correlation_visualizations'
corr_scatter_visualizations = [
    os.path.join(corr_visualizations_dir, file)
    for file in os.listdir(corr_visualizations_dir) if file.endswith('.png')
]
correlation_results_file = os.path.join(corr_visualizations_dir, 'correlation_results.csv')
correlation_results = pd.read_csv(correlation_results_file)

# Liste de tous les piézomètres
all_piezometres = list(stats_data['nom_piezo'].unique())

# Layout de l'application
app.layout = html.Div([
    # Onglets
    dcc.Tabs(id="tabs", value="gene-visual", children=[
        dcc.Tab(label="Visualisation des Données par Piézomètre", value="gene-visual"),
        dcc.Tab(label="Statistiques Descriptives par Piézomètre", value="stats-descriptives"),
        dcc.Tab(label="Clustering (Sans Lags)", value="clustering"),
        dcc.Tab(label="Tests de Corrélation", value="correlation-tests"),
        dcc.Tab(label="Corrélation Croisée", value="cross-corr"),
        dcc.Tab(label="Clustering (Avec Lags)", value="clustering-lags"),
        dcc.Tab(label="Matrices de Corrélation", value="corr-matrices"),
        dcc.Tab(label="Tests de Causalité de Granger", value="granger-tests"),
        dcc.Tab(label="Tests Chi-deux", value="chi2-tests"),
        dcc.Tab(label="Tests de Corrélation avec Lags", value="corr-lags"),
    ]),
    # Dropdown global pour sélectionner un piézomètre
    html.Div([
        html.Label("Sélectionnez un Piézomètre", style={'fontSize': '20px', 'marginBottom': '10px'}),
        dcc.Dropdown(
            id='global-piezometre-dropdown',
            options=[{'label': piezo, 'value': piezo} for piezo in all_piezometres],
            value=all_piezometres[0],
            style={'width': '50%'}
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    html.Div(id="tabs-content")

])

# Callback pour mettre à jour le contenu selon l'onglet sélectionné
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'), Input('global-piezometre-dropdown', 'value')]
)
def render_tab_content(tab, selected_piezometre):
    filtered_graphs = []  # Valeur par défaut pour les graphiques filtrés

    if tab == "gene-visual":
        normalized_piezometre = normalize_filename(selected_piezometre)
        graphs = gene_visual_graphs.get(normalized_piezometre, [])
        if graphs:
            return html.Div([
            html.H1(f"Visualisation des Données - {selected_piezometre}", style={'textAlign': 'center'}),
            html.Div([
                html.Iframe(
                    src=graph,
                    style={'width': '100%', 'height': '600px', 'marginBottom': '20px'}
                ) for graph in graphs
            ])
        ])
        else:
            return html.P(f"Aucun graphique disponible pour {selected_piezometre}.")
    
    elif tab == "stats-descriptives":
        filtered_data = stats_data[stats_data['nom_piezo'] == selected_piezometre]
        return html.Div([
            html.H1(f"Statistiques Descriptives - {selected_piezometre}", style={'textAlign': 'center'}),
            dash_table.DataTable(
                id='stats-table',
                columns=[{"name": i, "id": i} for i in filtered_data.columns],
                data=filtered_data.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '10px'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                page_size=10
            )
        ])
    
    elif tab == "clustering":
        filtered_graphs = [graph for graph in clustering_graphs if selected_piezometre in graph]
        if filtered_graphs:
            return html.Div([
                html.H1(f"Clustering des précipitations et variations (Sans Lags) - {selected_piezometre}", style={'textAlign': 'center'}),
                html.Div([
                    html.Img(src=path, style={'width': '100%', 'marginBottom': '20px'}) for path in filtered_graphs
                ])
            ])
        else:
            return html.P(f"Aucun graphique de clustering disponible pour {selected_piezometre}.")
    
    elif tab == "correlation-tests":
        normalized_piezometre = normalize_filename(selected_piezometre)
        scatter_graphs = [graph for graph in corr_scatter_visualizations if normalized_piezometre in graph]
        if scatter_graphs:
            return html.Div([
            html.H1(f"Tests de Corrélation - {selected_piezometre}", style={'textAlign': 'center'}),
            html.Div([
                html.Div([
                    html.H3(f"{row['type_averse']}"),
                    html.P(f"Corrélation : {row['correlation']:.4f}, P-value : {row['p_value']:.4e}")
                ])
                for _, row in correlation_results[correlation_results['piezometre'] == selected_piezometre].iterrows()
            ]),
            html.Div([
                html.Img(src=graph, style={'width': '100%', 'marginBottom': '20px'}) for graph in scatter_graphs
            ])
        ])
        else:
            return html.P(f"Aucun graphique de corrélation disponible pour {selected_piezometre}.")
    
    elif tab == "cross-corr":
        normalized_piezometre = normalize_filename(selected_piezometre)
        filtered_graphs = [graph for graph in cross_corr_graphs if normalized_piezometre in graph]
        if filtered_graphs:  # Vérifiez si des graphiques ont été trouvés
            return html.Div([
            html.H1(f"Corrélation Croisée - {selected_piezometre}", style={'textAlign': 'center'}),
            html.Div([
                html.Img(src=path, style={'width': '100%', 'marginBottom': '20px'}) for path in filtered_graphs
            ])
        ])
        else:  # Si aucun graphique n'est trouvé
            return html.P(f"Aucun graphique de corrélation croisée disponible pour {selected_piezometre}.")
        
    elif tab == "clustering-lags":
        normalized_piezometre = normalize_filename(selected_piezometre)
        graphs = clustering_lags_graphs.get(normalized_piezometre, [])
        if graphs:
            return html.Div([
            html.H1(f"Clustering (Avec Lags) - {selected_piezometre}", style={'textAlign': 'center'}),
            html.Div([
                html.Img(src=graph['path'], style={'width': '100%', 'marginBottom': '20px'})
                for graph in graphs
            ])
        ])
        else:
            return html.P(f"Aucun graphique de clustering avec lags disponible pour {selected_piezometre}.")
    
    elif tab == "corr-matrices":
        if selected_piezometre:  # Vérifiez que selected_piezometre n'est pas None
            normalized_piezometre = normalize_filename(selected_piezometre)
            filtered_graphs = [graph for graph in corr_matrices_graphs if normalized_piezometre in graph]
            if filtered_graphs:
                return html.Div([
                html.H1(f"Matrices de Corrélation - {selected_piezometre}", style={'textAlign': 'center'}),
                html.Div([
                    html.Iframe(src=path, style={'width': '100%', 'height': '600px', 'marginBottom': '20px'})
                    for path in filtered_graphs
                ])
            ])
            else:
                return html.P(f"Aucune matrice de corrélation disponible pour {selected_piezometre}.")
        else:
            return html.P("Veuillez sélectionner un piézomètre pour afficher les matrices de corrélation.")
    
    elif tab == "granger-tests":
        normalized_piezometre = normalize_filename(selected_piezometre)
        if 'nom_piezo' in granger_results.columns:
            filtered_data = granger_results[granger_results['nom_piezo'] == normalized_piezometre]
            print(selected_piezometre)
            if not filtered_data.empty:
                return html.Div([
                html.H1(f"Tests de Causalité de Granger - {selected_piezometre}", style={'textAlign': 'center'}),
                dash_table.DataTable(
                    id='granger-table',
                    columns=[{"name": i, "id": i} for i in filtered_data.columns],
                    data=filtered_data.to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'center', 'padding': '10px'},
                    style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                    page_size=10
                )
            ])
            else:
                print(selected_piezometre)
                return html.P(f"Aucune donnée de Granger disponible pour {selected_piezometre}.")
        else:
            return html.P("Erreur : la colonne 'nom_piezo' est introuvable dans les résultats.")
    
    elif tab == "chi2-tests":
        normalized_piezometre = normalize_filename(selected_piezometre)
        filtered_graphs = [graph for graph in chi2_visualizations if normalized_piezometre in graph]
        if filtered_graphs:
            return html.Div([
            html.H1(f"Tests Chi-deux - {selected_piezometre}", style={'textAlign': 'center'}),
            html.Div([
                html.Img(src=file_path, style={'width': '100%', 'marginBottom': '20px'})
                for file_path in filtered_graphs
            ])
        ])
        else:
            return html.P(f"Aucun graphique de test Chi-deux disponible pour {selected_piezometre}.")
    
    elif tab == "corr-lags":
        normalized_piezometre = normalize_filename(selected_piezometre)
        filtered_graphs = [graph for graph in corr_lag_visualizations if normalized_piezometre in graph]
        if filtered_graphs:
            return html.Div([
            html.H1(f"Tests de Corrélation avec Lags - {selected_piezometre}", style={'textAlign': 'center'}),
            html.Div([
                html.Img(src=graph, style={'width': '100%', 'marginBottom': '20px'}) for graph in filtered_graphs
            ])
        ])
        else:
            return html.P(f"Aucun graphique de corrélation avec lags disponible pour {selected_piezometre}.")
    
    return html.P("Contenu non disponible pour cet onglet.")
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Par défaut, utilisez le port 8050
    app.run_server(host='0.0.0.0', port=port)
    app.run_server(debug=True)