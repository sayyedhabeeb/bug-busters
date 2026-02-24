param(
    [switch]$SkipPipeline,
    [switch]$SkipPreprocessing,
    [switch]$SkipFeatureEngineering,
    [switch]$SkipTraining,
    [switch]$SkipEvaluation,
    [switch]$NoStartServices,
    [int]$ApiPort = 8000,
    [int]$DashboardPort = 8501
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path ".").Path

function Run-Step {
    param(
        [string]$Name,
        [string]$Command
    )

    Write-Host "==> $Name"
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name"
    }
}

if (-not $SkipPipeline) {
    $pipelineArgs = @()
    if ($SkipPreprocessing) { $pipelineArgs += "-SkipPreprocessing" }
    if ($SkipFeatureEngineering) { $pipelineArgs += "-SkipFeatureEngineering" }
    if ($SkipTraining) { $pipelineArgs += "-SkipTraining" }
    $pipelineArgText = ($pipelineArgs -join " ")

    Run-Step -Name "Pipeline (preprocessing/features/training)" -Command "powershell -ExecutionPolicy Bypass -File scripts/run_pipeline.ps1 $pipelineArgText"
}

if (-not $SkipEvaluation) {
    Run-Step -Name "Model Evaluation" -Command ".\venv\Scripts\python.exe -c `"from src.evaluation.engine import EvaluationEngine; EvaluationEngine().evaluate()`""
}

if ($NoStartServices) {
    Write-Host "Pipeline/evaluation complete. Service startup skipped."
    exit 0
}

Write-Host "==> Launching API and Dashboard in separate terminal windows..."

$apiCommand = "cd `"$projectRoot`"; .\venv\Scripts\python.exe -m uvicorn src.api.server:app --host 127.0.0.1 --port $ApiPort"
$uiCommand = "cd `"$projectRoot`"; .\venv\Scripts\python.exe -m streamlit run src/ui/app.py --server.port $DashboardPort --server.headless true --browser.gatherUsageStats false"

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $apiCommand) | Out-Null
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $uiCommand) | Out-Null

Write-Host ""
Write-Host "Project started."
Write-Host "API URL:        http://127.0.0.1:$ApiPort"
Write-Host "API Docs:       http://127.0.0.1:$ApiPort/docs"
Write-Host "Dashboard URL:  http://127.0.0.1:$DashboardPort"
Write-Host ""
Write-Host "Close the two opened PowerShell windows to stop services."
