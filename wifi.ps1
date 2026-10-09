$ErrorActionPreference = 'Stop'
$OUTPUT_FILE = Join-Path $PSScriptRoot 'wifi_credentials.json'

# --- Elevation admin auto ---
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '[*] Privileges insuffisants. Relance automatique en tant qu''administrateur...'
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host '[*] Recherche du Wi-Fi actuellement actif...'

$interface = netsh wlan show interfaces 2>$null
$ssid = ($interface | Select-String 'SSID' | Select-Object -First 1).Line
if (-not $ssid) {
    Write-Error 'Erreur : Vous n''etes connecte a aucun reseau Wi-Fi actuellement.'
    exit 1
}

$ssid = ($ssid -split ':', 2)[1].Trim()
Write-Host "[+] Reseau actif trouve : $ssid"

$profile = netsh wlan show profile name="$ssid" key=clear 2>$null
$keyLine = $profile | Select-String 'Key Content|Contenu de la cle' | Select-Object -First 1
if ($keyLine) {
    $password = ($keyLine.Line -split ':', 2)[1].Trim()
} else {
    $password = $null
}

if (-not $password) {
    $json = @(
        [pscustomobject]@{ ssid = $ssid; password = $null }
    ) | ConvertTo-Json -Depth 3
} else {
    $json = @(
        [pscustomobject]@{ ssid = $ssid; password = $password }
    ) | ConvertTo-Json -Depth 3
}

Set-Content -Path $OUTPUT_FILE -Encoding UTF8 -Value $json
Write-Host "[+] Termine ! Donnees enregistrees dans : $OUTPUT_FILE"
