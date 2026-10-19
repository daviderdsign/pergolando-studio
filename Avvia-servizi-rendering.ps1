$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$runtimeDir = Join-Path $projectRoot 'output/runtime'
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
function ServiceReady($port) {try { return (Invoke-RestMethod "http://127.0.0.1:$port/health" -TimeoutSec 2).status -eq 'ok' } catch { return $false }}
function WorkerRunning($pattern) { return [bool](Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object { $_.CommandLine -match $pattern -and $_.Name -match 'python|node' }) }
if (-not (ServiceReady 8090) -and -not (WorkerRunning 'python.*-u server\.py')) {
 Start-Process (Join-Path $projectRoot 'pergolando-geocalib-service/.venv/Scripts/python.exe') -ArgumentList '-u server.py' -WorkingDirectory (Join-Path $projectRoot 'pergolando-geocalib-service') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'geocalib.out.log') -RedirectStandardError (Join-Path $runtimeDir 'geocalib.err.log')
}
if (-not (ServiceReady 8080) -and -not (WorkerRunning 'node.*--env-file=\.env server\.js')) {
 Start-Process 'C:/Program Files/nodejs/node.exe' -ArgumentList '--env-file=.env server.js' -WorkingDirectory (Join-Path $projectRoot 'pergolando-blender-service') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'blender.out.log') -RedirectStandardError (Join-Path $runtimeDir 'blender.err.log')
}
Write-Output 'Avvio richiesto. GeoCalib puo richiedere tempo per caricare il modello. La demo verifica la disponibilita dal NAS.'
