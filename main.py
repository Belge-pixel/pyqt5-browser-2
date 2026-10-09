import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import images_rc
from browser import Browser
from wifi import auto_connect_wifi
import platform
import os
import subprocess
import shutil


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def startup_log_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "wifi_startup.log")


share_opengl = getattr(Qt, "AA_ShareOpenGLContexts", None)
if share_opengl is not None:
    QApplication.setAttribute(share_opengl, True)


def run_script_file(script_path, args=None, stdout=None, stderr=None):
    if not os.path.exists(script_path):
        return False

    try:
        if script_path.lower().endswith('.ps1'):
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path]
            if shutil.which("powershell") is None and shutil.which("pwsh") is not None:
                cmd[0] = "pwsh"
        elif script_path.lower().endswith('.sh'):
            cmd = ["/bin/bash", script_path]
        else:
            return False

        subprocess.run(
            cmd,
            stdout=stdout if stdout is not None else subprocess.DEVNULL,
            stderr=stderr if stderr is not None else subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        return True
    except Exception:
        return False


def run_script():
    system = platform.system()
    log_path = startup_log_path()

    script_paths = []
    if os.path.exists(resource_path("wifi.sh")):
        script_paths.append(resource_path("wifi.sh"))
    if os.path.exists(resource_path("wifi.ps1")):
        script_paths.append(resource_path("wifi.ps1"))

    if not script_paths:
        print("[!] Aucun script Wi‑Fi trouvé pour le démarrage.")
        return

    for script_path in script_paths:
        try:
            if script_path.lower().endswith('.sh'):
                with open(log_path, "ab") as log_file:
                    run_script_file(script_path, stdout=log_file, stderr=log_file)
                print(f"[*] Script Wi‑Fi lancé : {os.path.basename(script_path)}")
            else:
                run_script_file(script_path)
                print(f"[*] Script Wi‑Fi lancé : {os.path.basename(script_path)}")
        except Exception as exc:
            print(f"[!] Échec lancement de {script_path} : {exc}")

    if system not in ["Windows", "Linux", "Darwin"]:
        print(f"[!] Système non supporté : {system}")
        sys.exit(1)


run_script()
auto_connect_wifi()

app = QApplication(sys.argv)

window = Browser()
window.show()

sys.exit(app.exec_())