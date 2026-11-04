<#
modsource: ontolomerge_sumo_editor_v1_20261103
Public release.
Stops only this editor, gracefully; workspace changes remain durable.
#>
[CmdletBinding()]
param([int]$Port = 41772)
$ErrorActionPreference = 'Stop'
$editorUrl = "http://127.0.0.1:$Port"
$health = Invoke-RestMethod "$editorUrl/api/health" -TimeoutSec 3
if ($health.mode -ne 'sumo_editor') { throw 'This port is not a SUMO editor.' }
Invoke-RestMethod "$editorUrl/api/editor_shutdown" -Method Post -ContentType 'application/json' -Headers @{'X-OntoloMerge-Token'=$health.token} -Body '{}' | Out-Null
Write-Output 'SUMO editor stopped; workspace retained.'
