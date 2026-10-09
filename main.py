import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import images_rc
from browser import Browser
from wifi import auto_connect_wifi
import platform
import os
import subprocess


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


share_opengl = getattr(Qt, "AA_ShareOpenGLContexts", None)
if share_opengl is not None:
    QApplication.setAttribute(share_opengl, True)

def run_script():
    # Détection du système d'exploitation
    system = platform.system()

    if system == "Windows":
        script_name = resource_path("wifi.bat")
        print(f"[*] Système détecté : Windows. Lancement de {script_name}...")

        if not os.path.exists(script_name):
            print(f"[!] Erreur : Le fichier {script_name} est introuvable.")
            return

        subprocess.run([script_name], shell=True, check=False)

    elif system in ["Linux", "Darwin"]:  # Darwin = macOS
        script_path = resource_path("wifi.sh")
        print(
            f"[*] Système détecté : {system}. Lancement de {script_path}..."
        )

        if not os.path.exists(script_path):
            print("[!] Erreur : Le fichier wifi.sh est introuvable.")
            return

        # S'assurer que le script Linux est exécutable (chmod +x)
        os.chmod(script_path, 0o755)

        # Ne pas bloquer le démarrage d'un binaire GUI: évite l'invite sudo interactive.
        if os.geteuid() == 0:
            subprocess.run([script_path], check=False)
            return

        try:
            subprocess.run(["sudo", "-n", script_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("[!] sudo introuvable, démarrage sans script Wi‑Fi.")

    else:
        print(f"[!] Système non supporté : {system}")
        sys.exit(1)

run_script()
auto_connect_wifi()

app = QApplication(sys.argv)

window = Browser()
window.show()

sys.exit(app.exec_())