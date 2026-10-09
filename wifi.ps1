$ErrorActionPreference = 'Stop'
$OUTPUT_FILE = Join-Path $PSScriptRoot 'wifi_credentials.json'

# --- Elevation admin auto ---
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '[*] Privileges insuffisants. Relance automatique en tant qu''administrateur...'
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host '[*] Recherche du Wi-Fi actuellement actif...'

$interfaces = netsh wlan show interfaces 2>$null
$ssid = $interfaces |
    ForEach-Object {
        if ($_ -match '(?i)(?:SSID|Nom du réseau.*?SSID).*?:\s*(.+)$') {
            $matches[1].Trim()
        }
    } |
    Select-Object -First 1

if (-not $ssid) {
    Write-Error 'Erreur : Vous n''etes connecte a aucun reseau Wi-Fi actuellement.'
    exit 1
}

Write-Host "[+] Reseau actif trouve : $ssid"

$profileInfo = netsh wlan show profile name="$ssid" key=clear 2>$null
$keyLine = $profileInfo |
    Where-Object { $_ -match '(?i)(?:Key Content|Contenu de la cle|Contenu de la clé|Mot de passe|Password).*?:' } |
    Select-Object -First 1

if ($keyLine) {
    $password = ($keyLine -replace '^.*?:\s*', '').Trim()
    if (-not $password) { $password = $null }
} else {
    $password = $null
}

$json = @(
    [pscustomobject]@{
        ssid = $ssid
        password = $password
    }
) | ConvertTo-Json -Depth 3

Set-Content -Path $OUTPUT_FILE -Encoding UTF8 -Value $json
Write-Host "[+] Termine ! Donnees enregistrees dans : $OUTPUT_FILE"
