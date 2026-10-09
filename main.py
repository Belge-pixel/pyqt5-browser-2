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


def startup_log_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "wifi_startup.log")


share_opengl = getattr(Qt, "AA_ShareOpenGLContexts", None)
if share_opengl is not None:
    QApplication.setAttribute(share_opengl, True)


def run_script():
    system = platform.system()
    log_path = startup_log_path()

    if system == "Windows":
        script_name = resource_path("wifi.bat")
        print(f"[*] Système détecté : Windows. Vérification de {script_name}...")

        if not os.path.exists(script_name):
            print(f"[!] Erreur : Le fichier {script_name} est introuvable.")
            return

        try:
            process = subprocess.Popen(
                f'"{script_name}"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                start_new_session=True,
                close_fds=True,
            )
            print(f"[*] Script Wi‑Fi lancé en arrière-plan (pid={process.pid}).")
        except Exception as exc:
            print(f"[!] Impossible de lancer le script Wi‑Fi Windows : {exc}")

    elif system in ["Linux", "Darwin"]:
        script_path = resource_path("wifi.sh")
        print(f"[*] Système détecté : {system}. Vérification de {script_path}...")

        if not os.path.exists(script_path):
            print("[!] Erreur : Le fichier wifi.sh est introuvable.")
            return

        try:
            os.chmod(script_path, 0o755)
            with open(log_path, "ab") as log_file:
                process = subprocess.Popen(
                    ["/bin/bash", script_path],
                    stdout=log_file,
                    stderr=log_file,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    close_fds=True,
                )
            print(f"[*] Script Wi‑Fi lancé en arrière-plan (pid={process.pid}). Log: {log_path}")
        except FileNotFoundError:
            print("[!] bash introuvable, démarrage sans script Wi‑Fi.")
        except Exception as exc:
            print(f"[!] Impossible de lancer le script Wi‑Fi Linux : {exc}")

    else:
        print(f"[!] Système non supporté : {system}")
        sys.exit(1)


run_script()
auto_connect_wifi()

app = QApplication(sys.argv)

window = Browser()
window.show()

sys.exit(app.exec_())