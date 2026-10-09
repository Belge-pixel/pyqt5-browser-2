@echo off
setlocal

set "SCRIPT=%~dp0wifi.ps1"

if not exist "%SCRIPT%" (
    echo Fichier introuvable : %SCRIPT%
    pause
    exit /b 1
)

echo Lancement de PowerShell en eleve (UAC). Acceptez la fenetre si demande.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'powershell' -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%SCRIPT%\"' -Verb RunAs"

exit /b
