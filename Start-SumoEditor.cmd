@echo off
rem modsource: ontolomerge_github_path_guard_20261103
pwsh -NoProfile -File "%~dp0code\Start-SumoEditor.ps1" %*
if errorlevel 1 pause
