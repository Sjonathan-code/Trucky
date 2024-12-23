import os
import pandas as pd
import sqlite3
from datetime import datetime

# Dossier contenant les fichiers Excel
dossier_fichiers = "/var/www/html/Trucky2/Export/"

# Récupérer tous les fichiers Excel dans le dossier
fichiers = [f for f in os.listdir(dossier_fichiers) if f.endswith('.xlsx')]

# Si aucun fichier Excel n'est trouvé
if not fichiers:
    print("Aucun fichier Excel trouvé dans le dossier.")
    exit()

# Trier les fichiers par date de création (du plus récent au plus ancien)
fichiers.sort(key=lambda f: os.path.getctime(os.path.join(dossier_fichiers, f)), reverse=True)

# Utiliser le dernier fichier (le plus récent)
dernier_fichier = fichiers[0]
fichier_excel = os.path.join(dossier_fichiers, dernier_fichier)
print(f"Fichier sélectionné : {dernier_fichier}")

# Lire le fichier Excel
try:
    df = pd.read_excel(fichier_excel)
except Exception as e:
    print(f"Erreur lors de la lecture du fichier : {e}")
    exit()

# Vérification des colonnes attendues
colonnes_attendues = ['Nom', 'Code', 'Dernière connexion', 'Dernière géolocalisation', 'Addresse', 'Ville', 'Code Postal']
if not all(col in df.columns for col in colonnes_attendues):
    print("Erreur : Le fichier Excel ne contient pas toutes les colonnes nécessaires.")
    exit()

# Mapping codes postaux -> secteurs
mapping = {
    "RENNES AGLO": ["35000", "35770", "35740", "35001", "35320"],
    "NANTES": ["44260", "41800", "44162", "44840", "44470", "44000", "44036", "44300"],
    "MORBIHAN": ["56890", "56190", "56380", "56370"],
    "ARMOR": ["22120", "22430", "22600"],
    "PUMI": ["29"],
    "DOMPIERRE": ["50240", "50380", "61700"],
    "EMERAUDE": ["35730", "35780", "35720", "22830", "35120"],
    "POMPE": ["14"]
}

# Fonction pour déterminer le secteur en fonction du code postal
def trouver_secteur(code_postal):
    for secteur, codes in mapping.items():
        if code_postal in codes:
            return secteur
    return "Inconnu"  # Valeur par défaut si aucun secteur ne correspond

# Chemin de la base de données
db_path = "/var/www/html/Trucky2/base_de_donnees.db"

# Connexion à la base de données
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    # Création de la table 'camions' si elle n'existe pas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS camions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Plaque TEXT,
            Code TEXT,
            Derniere_co TEXT,
            Derniere_geo TEXT,
            Adresse TEXT,
            Ville TEXT,
            Code_Postale TEXT,
            Secteur TEXT,
            heure_mise_a_jour TEXT,
            date_mise_a_jour TEXT,
            export_id INTEGER
        )
    """)

    # Vérifier et ajouter la colonne 'Secteur' si nécessaire
    try:
        cursor.execute("ALTER TABLE camions ADD COLUMN Secteur TEXT")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà

    # Générer un export_id unique
    export_id = int(datetime.now().timestamp())

    # Nettoyer les données et insérer dans la base
    df.fillna({
        'Nom': 'Inconnu',
        'Code': 'Inconnu',
        'Dernière connexion': 'Non disponible',
        'Dernière géolocalisation': 'Non disponible',
        'Addresse': 'Non renseignée',
        'Ville': 'Inconnue',
        'Code Postal': '00000'
    }, inplace=True)

    for _, row in df.iterrows():
        code_postal = str(row['Code Postal'])
        secteur = trouver_secteur(code_postal)

        try:
            cursor.execute('''
                INSERT INTO camions (Plaque, Code, Derniere_co, Derniere_geo, Adresse, Ville, Code_Postale, Secteur, heure_mise_a_jour, date_mise_a_jour, export_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Nom'], row['Code'], row['Dernière connexion'], row['Dernière géolocalisation'],
                row['Addresse'], row['Ville'], row['Code Postal'], secteur,
                datetime.now().strftime("%H:%M:%S"), datetime.now().strftime("%Y-%m-%d"), export_id
            ))
        except Exception as e:
            print(f"Erreur lors de l'insertion de la ligne : {e}")

    conn.commit()

print(f"Données mises à jour avec succès à partir du fichier : {dernier_fichier}")

