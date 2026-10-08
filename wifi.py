import json
import os
import subprocess
import sys


def resource_path(relative_path):
    clean_relative = relative_path.lstrip("/")

    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        candidates = [
            os.path.join(base_path, clean_relative),
            os.path.join(base_path, *clean_relative.split("/")),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return candidates[0]

    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, clean_relative)


def auto_connect_wifi():
    file_path = resource_path("wifi_credentials.json")
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        return False

    if not isinstance(data, list):
        return False

    for entry in data:
        if not isinstance(entry, dict):
            continue

        ssid = (entry.get("ssid") or "").strip()
        password = entry.get("password")

        if not ssid:
            continue

        try:
            active = subprocess.run(
                ["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"],
                capture_output=True,
                text=True,
                check=False,
            )
            active_names = {line.strip() for line in active.stdout.splitlines() if line.strip()}

            if ssid in active_names:
                return True

            if password and password not in ("", "null", "None"):
                subprocess.run(
                    ["nmcli", "device", "wifi", "connect", ssid, "password", str(password)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            else:
                subprocess.run(
                    ["nmcli", "connection", "up", ssid],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            return True
        except Exception:
            continue

    return False


if __name__ == "__main__":
    auto_connect_wifi()
