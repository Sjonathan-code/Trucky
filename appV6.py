from flask import Flask, render_template, request
import sqlite3

# Création de l'application Flask
app = Flask(__name__)

# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('base_de_donnees.db')
    conn.row_factory = sqlite3.Row  # Accéder aux colonnes par leur nom
    return conn

# Route principale
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer le dernier export_id pour afficher les données par défaut
    cursor.execute("SELECT MAX(export_id) FROM camions")
    export_id = cursor.fetchone()[0]

    # Récupérer toutes les données du dernier export
    cursor.execute("SELECT * FROM camions WHERE export_id = ?", (export_id,))
    results = cursor.fetchall()

    # Récupérer tous les secteurs distincts pour les boutons
    cursor.execute("SELECT DISTINCT Secteur FROM camions WHERE export_id = ?", (export_id,))
    secteurs = [row['Secteur'] for row in cursor.fetchall()]

    conn.close()

    return render_template('index.html', results=results, secteurs=secteurs)

# Route pour la recherche
@app.route('/search', methods=['GET'])
def search():
    # Récupération des paramètres de recherche
    query = request.args.get('query', '')
    secteur = request.args.get('secteur', '')  # Filtre par secteur
    export_id = request.args.get('export_id', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtenir le dernier export_id si aucun export_id n'est spécifié
    if not export_id:
        cursor.execute("SELECT MAX(export_id) FROM camions")
        export_id = cursor.fetchone()[0]

    # Requête SQL de base
    sql = "SELECT * FROM camions WHERE export_id = ?"
    params = [export_id]

    # Ajout d'une recherche textuelle si une requête est fournie
    if query:
        sql += " AND (Plaque LIKE ? OR Code LIKE ? OR Derniere_co LIKE ? OR Derniere_geo LIKE ? OR Adresse LIKE ? OR Ville LIKE ? OR Code_Postale LIKE ?)"
        params += ['%' + query + '%'] * 7

    # Ajout d'un filtre par secteur si nécessaire
    if secteur:
        sql += " AND Secteur = ?"
        params.append(secteur)

    # Exécution de la requête
    cursor.execute(sql, params)
    results = cursor.fetchall()

    # Récupérer tous les secteurs distincts pour les boutons
    cursor.execute("SELECT DISTINCT Secteur FROM camions WHERE export_id = ?", (export_id,))
    secteurs = [row['Secteur'] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        'index.html', 
        results=results, 
        secteurs=secteurs, 
        selected_secteur=secteur, 
        query=query
    )

# Point d'entrée principal pour exécuter l'application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

