@echo off
rem modsource: ontolomerge_v04_public_20261105
pwsh -NoProfile -File "%~dp0code\Start-SumoEditor.ps1" %*
if errorlevel 1 pause
