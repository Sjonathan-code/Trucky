import time
import subprocess
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By

# Chemin vers geckodriver
driver_path = '/var/www/html/Trucky2/Extraction/geckodriver'

# Dossier de téléchargement
download_folder = '/root/Téléchargements/'  # Remplace par ton dossier de téléchargement
destination_folder = '/var/www/html/Trucky2/Export/'  # Remplace par ton dossier de destination
file_prefix = "Export de la mire béton du"  # Le début du nom du fichier

# Ouvrir Firefox avec Geckodriver
options = webdriver.FirefoxOptions()
options.set_preference("browser.download.folderList", 2)  # 2 signifie un dossier personnalisé
options.set_preference("browser.download.dir", download_folder)  # Dossier de téléchargement personnalisé
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")  # Pour accepter tous les fichiers à télécharger sans demander
options.set_preference("browser.download.manager.showWhenStarting", False)  # Pour ne pas afficher la fenêtre de téléchargement
options.set_preference("pdfjs.disabled", True)  # Désactiver le visualiseur PDF intégré de Firefox, si nécessaire

driver = webdriver.Firefox(executable_path=driver_path, options=options)

# Aller à la page
driver.get("https://bhr.wayzz.fr/beta/index.php")

# Attendre que la page soit chargée
time.sleep(2)

# Trouver les champs utilisateur et mot de passe
username_field = driver.find_element(By.ID, 'user')  # ID du champ utilisateur
password_field = driver.find_element(By.ID, 'pass')  # ID du champ mot de passe

# Remplir les champs avec des valeurs
username_field.send_keys('BHR')  # Remplace par ton identifiant
password_field.send_keys('BHR@tech35!')  # Remplace par ton mot de passe

# Trouver et cliquer sur le bouton de soumission
submit_button = driver.find_element(By.ID, 'submit')  # ID du bouton de soumission
submit_button.click()  # Cliquer sur le bouton de soumission

# Attendre que la page suivante soit chargée
time.sleep(7)

# Trouver et cliquer sur le bouton d'export
export_button = driver.find_element(By.ID, 'concrete-target-export')  # ID du bouton d'export
print("Clique sur le bouton d'export...")
export_button.click()  # Cliquer sur le bouton d'export

# Fonction pour vérifier si un fichier avec le début de nom donné est présent dans le dossier
def is_file_downloaded(file_prefix, folder_path):
    files = os.listdir(folder_path)
    for file in files:
        print(f"Vérification du fichier: {file}")  # Affiche les fichiers pour déboguer
        if file.startswith(file_prefix):  # Vérifier si le fichier commence par le préfixe
            print(f"Fichier trouvé: {file}")  # Affiche le fichier trouvé
            return file  # Retourne le nom du fichier trouvé
    return None

# Attendre que le fichier soit téléchargé
print("Attente du téléchargement du fichier...")
downloaded_file = None
while downloaded_file is None:
    downloaded_file = is_file_downloaded(file_prefix, download_folder)
    time.sleep(2)  # Vérifier toutes les 2 secondes

# Attendre un peu pour s'assurer que le fichier est complètement téléchargé
time.sleep(5)

# Déplacer le fichier téléchargé dans le dossier de destination
if downloaded_file:
    source_path = os.path.join(download_folder, downloaded_file)
    destination_path = os.path.join(destination_folder, downloaded_file)
    shutil.move(source_path, destination_path)  # Déplace le fichier
    print(f"Le fichier a été déplacé vers : {destination_path}")

# Fermer le navigateur après que le fichier ait été téléchargé et déplacé
print("Le téléchargement est terminé et le fichier a été déplacé. Fermeture du navigateur...")
driver.quit()

# À la fin du script, pour exécuter un autre programme
programme_a_executer = '/var/www/html/Trucky2/update_data_V3.py'  # Remplace par le chemin de ton programme

# Utiliser subprocess.run() pour exécuter un programme et capturer la sortie
try:
    result = subprocess.run(
        ['python3', programme_a_executer], 
        check=True, 
        capture_output=True,  # Capture la sortie standard et l'erreur standard
        text=True              # Pour que les sorties soient sous forme de texte
    )
    
    # Afficher la sortie du programme
    print(f"Sortie du programme : {result.stdout}")
    print(f"Erreurs (s'il y en a) : {result.stderr}")
    print("Le programme a été exécuté avec succès.")
    
except subprocess.CalledProcessError as e:
    print(f"Erreur lors de l'exécution du programme : {e}")
    print(f"Sortie du programme : {e.stdout}")
    print(f"Erreurs : {e.stderr}")
