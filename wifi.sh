#!/bin/bash

OUTPUT_FILE="wifi_credentials.json"

# ---- AUTO-ÉLÉVATION DES PRIVILÈGES ----
if [ "$EUID" -ne 0 ]; then
    echo "[*] Privilèges insuffisants. Relance automatique avec sudo..."
    exec sudo "$0" "$@"
    exit $?
fi

# ---- VÉRIFICATION DES OUTILS ----
if ! command -v nmcli &> /dev/null; then
    echo "[!] Erreur : 'nmcli' (NetworkManager) n'est pas installé."
    exit 1
fi

echo "[*] Recherche du Wi-Fi actuellement actif..."

# 1. Récupérer le nom (SSID) du Wi-Fi actif uniquement
CURRENT_SSID=$(nmcli -t -f ACTIVE,SSID dev wifi | grep '^yes:' | cut -d':' -f2)

if [ -z "$CURRENT_SSID" ]; then
    echo "[!] Erreur : Vous n'êtes connecté à aucun réseau Wi-Fi actuellement."
    exit 1
fi

echo "[+] Réseau actif trouvé : $CURRENT_SSID"

# 2. Récupérer le mot de passe associé à ce réseau spécifique
PASSWORD=$(nmcli -s -g 802-11-wireless-security.psk connection show "$CURRENT_SSID" 2>/dev/null)

# 3. Écriture propre dans le fichier JSON
cat <<EOF > "$OUTPUT_FILE"
[
  {
    "ssid": "$CURRENT_SSID",
    "password": "${PASSWORD:-null}"
  }
]
EOF

echo "[+] Terminé ! Données enregistrées dans : $OUTPUT_FILE"
