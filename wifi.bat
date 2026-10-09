@echo off
setlocal enabledelayedexpansion

set "OUTPUT_FILE=wifi_credentials.json"

:: ---- AUTO-ÉLÉVATION DES PRIVILÈGES ----
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Privileges insuffisants. Relance automatique en tant qu'administrateur...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [*] Recherche du Wi-Fi actuellement actif...

:: 1. Récupérer le nom (SSID) du Wi-Fi actif uniquement
set "CURRENT_SSID="
for /f "tokens=2 delims=:" %%A in ('netsh wlan show interfaces ^| findstr /c:" SSID"') do (
    set "CURRENT_SSID=%%A"
    :: Supprimer l'espace initial laissé par netsh
    set "CURRENT_SSID=!CURRENT_SSID:~1!"
)

if "%CURRENT_SSID%"=="" (
    echo [!] Erreur : Vous n'etes connecte a aucun reseau Wi-Fi actuellement.
    exit /b 1
)

echo [+] Reseau actif trouve : %CURRENT_SSID%

:: 2. Récupérer le mot de passe associé à ce réseau spécifique
set "PASSWORD=null"
for /f "tokens=2 delims=:" %%B in ('netsh wlan show profile name^="%CURRENT_SSID%" key^=clear ^| findstr /c:"Contenu de la cle" /c:"Key Content"') do (
    set "PASSWORD=%%B"
    set "PASSWORD=!PASSWORD:~1!"
)

:: 3. Écriture propre dans le fichier JSON
echo [> "%OUTPUT_FILE%"
echo   {>> "%OUTPUT_FILE%"
echo     "ssid": "%CURRENT_SSID%",>> "%OUTPUT_FILE%"
if "%PASSWORD%"=="null" (
    echo     "password": null>> "%OUTPUT_FILE%"
) else (
    echo     "password": "%PASSWORD%">> "%OUTPUT_FILE%"
)
echo   }>> "%OUTPUT_FILE%"
echo ]>> "%OUTPUT_FILE%"

echo [+] Termine ! Donnees enregistrees dans : %OUTPUT_FILE%
