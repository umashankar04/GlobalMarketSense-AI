$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot
$env:PYTHONPATH = '.'

$python = 'C:/Users/UMASHANKAR/AppData/Local/Programs/Python/Python314/python.exe'

Write-Host '[1/3] Starting API on http://localhost:8000 ...'
Start-Process -FilePath $python -ArgumentList @('-m','uvicorn','backend.main:app','--host','0.0.0.0','--port','8000') -WorkingDirectory $PSScriptRoot

Start-Sleep -Seconds 3
Write-Host '[2/3] Opening localhost dashboard ...'
Start-Process 'http://localhost:8000/'
Start-Process 'http://localhost:8000/api/health'

Write-Host 'GlobalMarketSense AI started.'
Write-Host 'Dashboard: http://localhost:8000/'
Write-Host 'If already running, close old Python processes first.'
