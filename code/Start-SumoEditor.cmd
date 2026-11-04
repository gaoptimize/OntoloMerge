@echo off
rem modsource: ontolomerge_sumo_editor_v1_20261103
rem Public release.
pwsh -NoProfile -File "%~dp0Start-SumoEditor.ps1" %*
if errorlevel 1 pause
