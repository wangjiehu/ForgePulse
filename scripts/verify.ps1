$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendRoot = Join-Path $projectRoot "app\backend"
$frontendRoot = Join-Path $projectRoot "app\frontend"

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "Conda was not found in PATH."
}

$environments = conda env list --json | ConvertFrom-Json
if (-not ($environments.envs | Where-Object { (Split-Path $_ -Leaf) -eq "happy" })) {
    throw "The required Conda environment 'happy' was not found."
}

Write-Host "[1/6] Backend tests"
Push-Location $backendRoot
try {
    conda run -n happy python -m pytest -q
} finally {
    Pop-Location
}

Write-Host "[2/6] Golden and robustness evaluation"
Push-Location $projectRoot
try {
    conda run -n happy python evaluation\evaluate_cases.py
} finally {
    Pop-Location
}

Write-Host "[3/6] Frontend clean install"
Push-Location $frontendRoot
try {
    npm ci

    Write-Host "[4/6] Frontend production build"
    npm run build

    Write-Host "[5/6] Dependency audit"
    npm audit --audit-level=high

    Write-Host "[6/6] Frontend smoke"
    npm run smoke
} finally {
    Pop-Location
}

Write-Host "ForgePulse verification passed."
