import pandas as pd
from scipy.stats import chi2_contingency
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Fonction pour normaliser les noms de fichiers
def normalize_filename(name):
    """Remplace les espaces et caractères spéciaux par des underscores."""
    return name.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")

# Charger les données nettoyées avec les colonnes ajoutées
data = pd.read_csv('./data/data_cleaned_outliers.csv')

# Créer un dossier pour enregistrer les visualisations
output_dir = './assets/chi2_visualizations'
os.makedirs(output_dir, exist_ok=True)

# Initialiser une liste pour stocker les résultats
chi2_results = []

# Obtenir la liste unique des piézomètres
piezometres = data['nom_piezo'].unique()

# Effectuer le test Chi-deux pour chaque piézomètre
for piezometre in piezometres:
    print(f"\nPiézomètre : {piezometre}")
    
    # Filtrer les données pour le piézomètre en cours
    piezo_data = data[data['nom_piezo'] == piezometre]
    
    # Créer une table de contingence entre 'type_averse' et 'niveau_categorise'
    contingency_table = pd.crosstab(piezo_data['type_averse'], piezo_data['niveau_categorise'])
    
    # Réaliser le test de Chi-deux
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    
    # Enregistrer les résultats dans une liste
    chi2_results.append({
        'piezometre': normalize_filename(piezometre),
        'chi2': chi2,
        'p_value': p,
        'dof': dof,
        'dependent': p < 0.05
    })
    
    # Visualisation de la table de contingence pour le piézomètre en cours
    plt.figure(figsize=(10, 6))
    heatmap = sns.heatmap(contingency_table, annot=True, fmt="d", cmap="coolwarm", cbar=True)
    plt.title(f"Type d'averse vs Niveau des nappes\n(Piézomètre : {piezometre})")
    plt.xlabel("Niveau des nappes (catégorisé)")
    plt.ylabel("Type d'averse")
    
    # Ajouter les résultats du Chi-deux sur le graphique
    plt.text(
        0.5, -0.2,
        f"Chi2 : {chi2:.4f} | p-value : {p:.4e} | Dépendance : {'Oui' if p < 0.05 else 'Non'}",
        transform=plt.gca().transAxes,
        horizontalalignment='center', fontsize=10, color="black"
    )
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, f"chi2_{normalize_filename(piezometre)}.png")
    plt.savefig(output_file)
    plt.close()

# Sauvegarder les résultats dans un fichier CSV
chi2_results_df = pd.DataFrame(chi2_results)
chi2_results_file = os.path.join('./assets', 'chi2_results.csv')
chi2_results_df.to_csv(chi2_results_file, index=False)

print(f"Les résultats des tests Chi-deux ont été sauvegardés dans '{chi2_results_file}'.")