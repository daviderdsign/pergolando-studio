$ErrorActionPreference='Stop'
$launcher=Join-Path $PSScriptRoot 'Avvia-servizi-rendering.ps1'
$action=New-ScheduledTaskAction -Execute "$env:WINDIR/System32/WindowsPowerShell/v1.0/powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$launcher`"" -WorkingDirectory $PSScriptRoot
$login=New-ScheduledTaskTrigger -AtLogOn -User ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
$retry=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1)
$principal=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 2)
Register-ScheduledTask -TaskName 'Pergolando-Servizi-Rendering' -Action $action -Trigger @($login,$retry) -Principal $principal -Settings $settings -Description 'Avvia Blender e GeoCalib al login e recupera i processi arrestati ogni minuto.' -Force | Out-Null
Start-ScheduledTask -TaskName 'Pergolando-Servizi-Rendering'
Get-ScheduledTask -TaskName 'Pergolando-Servizi-Rendering' | Select-Object TaskName,State
