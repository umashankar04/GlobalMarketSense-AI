# GlobalMarketSense AI - Web App Runner
# Run the professional dashboard with sentiment and risk analytics

param(
    [int]$Port = 8000,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot
$env:PYTHONPATH = '.'

$python = 'C:/Users/UMASHANKAR/AppData/Local/Programs/Python/Python314/python.exe'

# Step 1: Kill any existing server on the port
Write-Host "[1/3] Stopping existing GlobalMarketSense API process (if any) ..."
Get-CimInstance Win32_Process |
    Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*uvicorn*backend.main:app*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Start-Sleep -Seconds 1

# Step 2: Start the API server
Write-Host "[2/3] Starting API on http://localhost:$Port ..."
Start-Process -FilePath $python -ArgumentList @('-m','uvicorn','backend.main:app','--host','0.0.0.0','--port',"$Port") -WorkingDirectory $PSScriptRoot

# Step 3: Wait for health check
Write-Host '[3/3] Waiting for API health check (up to 60 seconds) ...'
$ready = $false
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:$Port/api/health" -UseBasicParsing
        if ($res.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
    }
}

if (-not $ready) {
    throw "API did not become ready on http://localhost:$Port/api/health"
}

# Step 4: Open browser if requested
if (-not $NoBrowser) {
    Write-Host 'Opening dashboard in browser ...'
    Start-Process "http://localhost:$Port/"
}

Write-Host ""
Write-Host "GlobalMarketSense web app is running"
Write-Host "Dashboard: http://localhost:$Port/"
Write-Host "Health: http://localhost:$Port/api/health"
Write-Host ""
