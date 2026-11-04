<#
modsource: ontolomerge_sumo_editor_v1_20261103
Public release.
Starts the SUMO editor through Python Guardian, then opens its local URL.
#>
[CmdletBinding()]
param([switch]$NoOpen, [int]$Port = 41772, [string]$GuardianPath = $env:PYGUARDIAN_CMD)
$ErrorActionPreference = 'Stop'
if ($Port -le 10000 -or $Port -gt 65535) { throw 'Choose an ephemeral port above 10000.' }
$editorUrl = "http://127.0.0.1:$Port"
$health = $null
try { $health = Invoke-RestMethod "$editorUrl/api/health" -TimeoutSec 2 } catch {}
if ($health -and $health.mode -ne 'sumo_editor') { throw "Port $Port belongs to another application. Choose another -Port." }
if (-not $health) {
    $guardian = $GuardianPath
    if (-not $guardian) {
        $guardianCommand = Get-Command PyGuard.cmd -ErrorAction SilentlyContinue
        if ($guardianCommand) { $guardian = $guardianCommand.Source }
    }
    if (-not $guardian) { throw 'Set PYGUARDIAN_CMD or pass -GuardianPath pointing to PyGuard.cmd. See the guide for portable Python startup.' }
    if (-not (Test-Path -LiteralPath $guardian)) { throw 'Python Guardian is required. Repair its installation before running this editor.' }
    & $guardian --no-preflight --keep never --detach "$PSScriptRoot\serve_sumo_editor.py" --port $Port
    if ($LASTEXITCODE -ne 0) { throw 'Guardian did not accept the editor job.' }
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        Start-Sleep -Milliseconds 500
        try { $health = Invoke-RestMethod "$editorUrl/api/health" -TimeoutSec 2; break } catch {}
    }
    if (-not $health -or $health.mode -ne 'sumo_editor') { throw 'Editor did not become ready. Check the Guardian queue/log; a long-running supervised job may be ahead of it.' }
}
Write-Output "OntoloMerge SUMO editor: $editorUrl/"
if (-not $NoOpen) { Start-Process "$editorUrl/" }
