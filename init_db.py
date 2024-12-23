import sqlite3

# Connexion à la base SQLite
conn = sqlite3.connect("base_de_donnees.db")
cursor = conn.cursor()

# Supprimer la table 'camions' si elle existe déjà
cursor.execute("DROP TABLE IF EXISTS camions")

# Création de la table 'camions' avec la bonne structure
cursor.execute('''
CREATE TABLE IF NOT EXISTS camions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plaque TEXT NOT NULL,
    Code TEXT NOT NULL,
    Derniere_co TEXT NOT NULL,
    Derniere_geo TEXT NOT NULL,
    Adresse TEXT NOT NULL,
    Ville TEXT NOT NULL,
    Code_Postale INT NOT NULL,
    date_mise_a_jour TEXT NOT NULL,
    heure_mise_a_jour TEXT NOT NULL,
    export_id INTEGER
)
''')

print("Table 'camions' supprimée et recréée avec succès avec le champ export_id.")

# Sauvegarde et fermeture
conn.commit()
conn.close()

