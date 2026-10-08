import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
EXECUTABLE_NAME = "OdemBrowser"


def resolve_python_cmd():
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return [str(venv_python)]

    for candidate in ("python3", "python"):
        if shutil.which(candidate):
            return [candidate]

    return [sys.executable]


def run(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.check_call(cmd)


def add_data_arg(src: str, dest: str):
    # PyInstaller expects different separators on Windows and Linux
    if os.name == "nt":
        return ["--add-data", f"{src};{dest}"]
    return ["--add-data", f"{src}:{dest}"]


def build():
    python_cmd = resolve_python_cmd()

    cmd = [
        *python_cmd,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--windowed",
        "--name",
        EXECUTABLE_NAME,
        "--collect-all",
        "PyQtWebEngine",
        "--hidden-import",
        "PyQt5.sip",
        "--hidden-import",
        "PyQt5.QtNetwork",
        "--hidden-import",
        "PyQt5.QtWebEngineWidgets",
    ]

    for src, dest in [
        ("browser.ui", "."),
        ("assets", "assets"),
        ("icons", "icons"),
        ("logo", "logo"),
        ("home.html", "."),
        ("index.html", "."),
        ("wifi_credentials.json", "."),
    ]:
        if (ROOT / src).exists():
            cmd.extend(add_data_arg(str(src), dest))

    cmd.append("main.py")
    run(cmd)

    exe_path = DIST / EXECUTABLE_NAME
    if not exe_path.exists():
        exe_path = DIST / f"{EXECUTABLE_NAME}.exe" if os.name == "nt" else DIST / EXECUTABLE_NAME

    print("\nBuild completed.")
    print(f"Executable available in: {exe_path}")


if __name__ == "__main__":
    build()
