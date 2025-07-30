@echo off
:: Trouver le chemin du dossier actuel
cd /d "%~dp0/scripts/src"

:: Lancer le script Python intro
python intro.py

exit
