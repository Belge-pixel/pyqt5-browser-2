import os
import shutil
import stat
import subprocess
from pathlib import Path

APP_NAME = "Odem"
APP_NAME_ALIASES = [APP_NAME, "OdemBrowser"]
PROJECT_DIR = Path(__file__).resolve().parent

# Prefer an already built executable.
EXECUTABLE_CANDIDATES = [
    PROJECT_DIR / "dist" / name
    for name in APP_NAME_ALIASES
] + [
    PROJECT_DIR / name for name in APP_NAME_ALIASES
] + [
    PROJECT_DIR / "build" / name for name in APP_NAME_ALIASES
]

ICON_CANDIDATES = [
    PROJECT_DIR / "logo" / "odem.png",
    PROJECT_DIR / "logo" / "Odem.ico",
    PROJECT_DIR / "Odem.ico",
    PROJECT_DIR / "logo" / "logo.png",
]


def find_executable():
    for path in EXECUTABLE_CANDIDATES:
        if path.exists() and path.is_file():
            return path.resolve()
    return None


def find_icon():
    for path in ICON_CANDIDATES:
        if path.exists():
            return path.resolve()
    return None


def install_icon(icon_source: Path):
    # Always use the real project logo directly to avoid an old cached icon appearing.
    return icon_source.resolve()


def remove_stale_files():
    # Delete only this app's launcher and stale icon copies, never all application entries.
    stale_paths = [
        Path.home() / ".icons" / f"{name}.png" for name in APP_NAME_ALIASES
    ] + [
        Path.home() / ".local" / "share" / "icons" / f"{name}.png" for name in APP_NAME_ALIASES
    ] + [
        Path.home() / ".local" / "share" / "pixmaps" / f"{name}.png" for name in APP_NAME_ALIASES
    ] + [
        Path.home() / ".local" / "share" / "applications" / f"{name}.desktop" for name in APP_NAME_ALIASES
    ] + [
        Path.home() / "Desktop" / f"{name}.desktop" for name in APP_NAME_ALIASES
    ]
    for path in stale_paths:
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass


def refresh_desktop_cache():
    user_apps_dir = Path.home() / ".local" / "share" / "applications"
    user_apps_dir.mkdir(parents=True, exist_ok=True)

    for cmd in [
        ["update-desktop-database", str(user_apps_dir)],
        ["gtk-update-icon-cache", "-f", str(Path.home() / ".local" / "share" / "icons")],
    ]:
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

    # Only remove stale caches related to the app, not all desktop entries.
    cache_cleanup = [
        "find ~/.cache -maxdepth 3 -type f -name '*.kcache' -delete 2>/dev/null || true",
    ]
    for shell_cmd in cache_cleanup:
        try:
            subprocess.run(["bash", "-lc", shell_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

    for path in [
        Path.home() / ".icons" / f"{APP_NAME}.png",
        Path.home() / ".local" / "share" / "icons" / f"{APP_NAME}.png",
        Path.home() / ".local" / "share" / "pixmaps" / f"{APP_NAME}.png",
    ]:
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass


def create_desktop_file(exec_path: Path, icon_path: Path):
    remove_stale_files()
    user_apps_dir = Path.home() / ".local" / "share" / "applications"
    desktop_shortcut_path = Path.home() / "Desktop" / f"{APP_NAME}.desktop"
    user_apps_dir.mkdir(parents=True, exist_ok=True)
    desktop_shortcut_path.parent.mkdir(parents=True, exist_ok=True)

    # .desktop files must quote paths containing spaces.
    exec_cmd = f'"{exec_path}"'
    content = f"""[Desktop Entry]
Type=Application
Version=1.0
Name={APP_NAME}
Comment=Navigateur Web Odem
Exec={exec_cmd}
Path={PROJECT_DIR}
Icon={icon_path}
Terminal=false
Categories=Network;WebBrowser;
StartupWMClass={APP_NAME}
TryExec={exec_path}
MimeType=
"""

    user_desktop_file = user_apps_dir / f"{APP_NAME}.desktop"
    for target in (user_desktop_file, desktop_shortcut_path):
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(target, os.stat(target).st_mode | stat.S_IEXEC)

    # Optional system-wide install if running as root.
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        system_apps_dir = Path("/usr/share/applications")
        system_apps_dir.mkdir(parents=True, exist_ok=True)
        system_desktop = system_apps_dir / f"{APP_NAME}.desktop"
        with open(system_desktop, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(system_desktop, os.stat(system_desktop).st_mode | stat.S_IEXEC)

    refresh_desktop_cache()
    return user_desktop_file, desktop_shortcut_path


def launch_application(exec_path: Path):
    try:
        subprocess.Popen(
            [str(exec_path)],
            cwd=str(PROJECT_DIR),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print(f"[+] Application lancée : {exec_path}")
    except Exception as exc:
        print(f"[!] Impossible de lancer l'application automatiquement : {exc}")


if __name__ == "__main__":
    exec_path = find_executable()
    icon_source = find_icon()

    if icon_source is None:
        raise FileNotFoundError("Aucune icône trouvée dans le dossier 'logo'.")

    icon_path = install_icon(icon_source)

    if exec_path is None:
        user_desktop_file, desktop_shortcut_path = create_desktop_file(
            exec_path=PROJECT_DIR / APP_NAME,
            icon_path=icon_path,
        )
        print(f"[!] Exécutable introuvable. Le lanceur a été créé, mais il faut d'abord compiler l'application.")
        print(f"[+] Fichier de menu : {user_desktop_file}")
        print(f"[+] Raccourci bureau : {desktop_shortcut_path}")
        raise SystemExit(1)

    user_desktop_file, desktop_shortcut_path = create_desktop_file(exec_path, icon_path)

    print(f"[+] Fichier de menu créé : {user_desktop_file}")
    print(f"[+] Raccourci bureau créé : {desktop_shortcut_path}")
    print(f"[+] Icône utilisée : {icon_path}")
    print(f"[+] Binaire vérifié : {exec_path}")

    # Launch automatically after creation.
    launch_application(exec_path)
    print("[*] Le menu Ubuntu a été rafraîchi et l'application a été lancée.")
