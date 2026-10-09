@echo off
setlocal enabledelayedexpansion

set "OUTPUT_FILE=%~dp0wifi_credentials.json"

:: ---- AUTO-ÉLÉVATION DES PRIVILÈGES ----
net session >nul 2>&1
if errorlevel 1 (
    echo [*] Privileges insuffisants. Relance automatique en tant qu'administrateur...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '""%~f0""' -Verb RunAs"
    exit /b
)

echo [*] Recherche du Wi-Fi actuellement actif...

powershell -NoProfile -ExecutionPolicy Bypass -Command "
$interfaces = netsh wlan show interfaces;
$ssid = ($interfaces | Select-String 'SSID').Line.Split(':')[-1].Trim();
if (-not $ssid) { Write-Error 'Aucun reseau Wi-Fi actif.'; exit 1 }
$profile = netsh wlan show profile name=\"$ssid\" key=clear;
$keyLine = $profile | Select-String 'Key Content|Contenu de la cle' | Select-Object -First 1;
if ($keyLine) { $password = $keyLine.Line.Split(':')[-1].Trim() } else { $password = $null }
$json = @([pscustomobject]@{ ssid = $ssid; password = $password }) | ConvertTo-Json -Depth 3;
Set-Content -Path \"%OUTPUT_FILE%\" -Encoding UTF8 -Value $json;
Write-Host \"[+] Reseau actif trouve : $ssid\";
Write-Host \"[+] Termine ! Donnees enregistrees dans : %OUTPUT_FILE%\";"

exit /b %errorlevel%
