#!/bin/bash

OUTPUT_FILE="$(dirname "$0")/wifi_credentials.json"

# Si l'utilisateur n'est pas root, essayer une élévation non interactive sans bloquer.
if [ "$EUID" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then
        echo "[*] Élévation non interactive demandée..."
        exec sudo -n "$0" "$@"
    fi
    echo "[*] Pas de privilège root ni sudo non interactif disponible; continuation sans relance automatique."
fi

# ---- VÉRIFICATION DES OUTILS ----
if ! command -v nmcli >/dev/null 2>&1; then
    echo "[!] Erreur : 'nmcli' (NetworkManager) n'est pas installé."
    exit 1
fi

echo "[*] Recherche du Wi-Fi actuellement actif..."

# 1. Récupérer le nom (SSID) du Wi-Fi actif uniquement
CURRENT_SSID=$(nmcli -t -f ACTIVE,SSID dev wifi 2>/dev/null | awk -F: '$1 == "yes" {print $2; exit}')

if [ -z "$CURRENT_SSID" ]; then
    echo "[!] Erreur : Vous n'êtes connecté à aucun réseau Wi‑Fi actuellement."
    exit 1
fi

echo "[+] Réseau actif trouvé : $CURRENT_SSID"

# 2. Récupérer le mot de passe associé au réseau spécifique
PASSWORD=$(nmcli -s -g 802-11-wireless-security.psk connection show "$CURRENT_SSID" 2>/dev/null | head -n 1)
if [ -z "$PASSWORD" ]; then
    PASSWORD="null"
fi

# 3. Écriture propre dans le fichier JSON
cat <<EOF > "$OUTPUT_FILE"
[
  {
    "ssid": "$CURRENT_SSID",
    "password": "$PASSWORD"
  }
]
EOF

echo "[+] Terminé ! Données enregistrées dans : $OUTPUT_FILE"
