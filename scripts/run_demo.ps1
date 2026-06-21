$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runtimeDir = Join-Path $projectRoot ".runtime"
$frontendRoot = Join-Path $projectRoot "app\frontend"
$backendRoot = Join-Path $projectRoot "app\backend"

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

if (-not (Test-Path (Join-Path $frontendRoot "node_modules"))) {
    Push-Location $frontendRoot
    try {
        npm ci
    } finally {
        Pop-Location
    }
}

$condaInfo = conda env list --json | ConvertFrom-Json
$happyEnvironment = $condaInfo.envs | Where-Object { (Split-Path $_ -Leaf) -eq "happy" } | Select-Object -First 1
if (-not $happyEnvironment) {
    throw "The required Conda environment 'happy' was not found."
}
$pythonExecutable = Join-Path $happyEnvironment "python.exe"
$nodeExecutable = (Get-Command node -ErrorAction Stop).Source
$viteEntry = Join-Path $frontendRoot "node_modules\vite\bin\vite.js"

$backendLog = Join-Path $runtimeDir "backend.out.log"
$backendErrorLog = Join-Path $runtimeDir "backend.error.log"
$frontendLog = Join-Path $runtimeDir "frontend.out.log"
$frontendErrorLog = Join-Path $runtimeDir "frontend.error.log"

$backend = Start-Process `
    -FilePath $pythonExecutable `
    -ArgumentList @("-m", "uvicorn", "forgepulse_api.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory $backendRoot `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErrorLog `
    -WindowStyle Hidden `
    -PassThru

$frontend = Start-Process `
    -FilePath $nodeExecutable `
    -ArgumentList @($viteEntry, "--host", "127.0.0.1", "--port", "5173") `
    -WorkingDirectory $frontendRoot `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendErrorLog `
    -WindowStyle Hidden `
    -PassThru

@{
    backend_pid = $backend.Id
    frontend_pid = $frontend.Id
    backend_url = "http://127.0.0.1:8000"
    frontend_url = "http://127.0.0.1:5173"
} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $runtimeDir "services.json")

Write-Host "ForgePulse started:"
Write-Host "  UI:  http://127.0.0.1:5173"
Write-Host "  API: http://127.0.0.1:8000"
Write-Host "  State: $runtimeDir\services.json"
