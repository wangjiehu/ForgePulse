$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$statePath = Join-Path $projectRoot ".runtime\services.json"

if (-not (Test-Path $statePath)) {
    Write-Host "No ForgePulse runtime state was found."
    exit 0
}

$state = Get-Content -Raw $statePath | ConvertFrom-Json
foreach ($processId in @($state.backend_pid, $state.frontend_pid)) {
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $processId -Force
        Write-Host "Stopped process $processId."
    }
}

Remove-Item -LiteralPath $statePath -Force
