import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import images_rc
from browser import Browser
from wifi import auto_connect_wifi
import platform
import os
import subprocess


share_opengl = getattr(Qt, "AA_ShareOpenGLContexts", None)
if share_opengl is not None:
    QApplication.setAttribute(share_opengl, True)

def run_script():
    # Détection du système d'exploitation
    system = platform.system()

    if system == "Windows":
        script_name = "wifi.bat"
        print(f"[*] Système détecté : Windows. Lancement de {script_name}...")

        # Vérification de l'existence du fichier
        if not os.path.exists(script_name):
            print(f"[!] Erreur : Le fichier {script_name} est introuvable.")
            sys.exit(1)

        # Sous Windows, l'élévation est gérée directement à l'intérieur du .bat via PowerShell
        subprocess.run([script_name], shell=True)

    elif system in ["Linux", "Darwin"]:  # Darwin = macOS
        script_name = "./wifi.sh"
        print(
            f"[*] Système détecté : {system}. Lancement de {script_name}..."
        )

        if not os.path.exists("wifi.sh"):
            print("[!] Erreur : Le fichier wifi.sh est introuvable.")
            sys.exit(1)

        # S'assurer que le script Linux est exécutable (chmod +x)
        os.chmod("wifi.sh", 0o755)

        # Pour Linux, on tente de pré-élever avec sudo si l'utilisateur n'est pas root
        if os.geteuid() != 0:
            print("[*] Passage en mode sudo...")
            subprocess.run(["sudo", script_name])
        else:
            subprocess.run([script_name])

    else:
        print(f"[!] Système non supporté : {system}")
        sys.exit(1)

run_script()
auto_connect_wifi()

app = QApplication(sys.argv)

window = Browser()
window.show()

sys.exit(app.exec_())