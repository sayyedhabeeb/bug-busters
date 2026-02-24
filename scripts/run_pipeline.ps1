param(
    [switch]$SkipPreprocessing,
    [switch]$SkipFeatureEngineering,
    [switch]$SkipTraining
)

$ErrorActionPreference = "Stop"

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

if (-not $SkipPreprocessing) {
    Run-Step -Name "Data Preprocessing" -Command ".\venv\Scripts\python.exe scripts/run_preprocessing.py"
}

if (-not $SkipFeatureEngineering) {
    Run-Step -Name "Feature Engineering" -Command ".\venv\Scripts\python.exe scripts/run_feature_engineering.py"

    # Keep compatibility with modules that read outputs/features/*
    $sourceFeatureDir = "data\processed\features"
    $targetFeatureDir = "outputs\features"
    if (-not (Test-Path $targetFeatureDir)) {
        New-Item -ItemType Directory -Path $targetFeatureDir | Out-Null
    }
    if (Test-Path "$sourceFeatureDir\feature_matrix.csv") {
        Copy-Item "$sourceFeatureDir\feature_matrix.csv" "$targetFeatureDir\feature_matrix.csv" -Force
    }
    if (Test-Path "$sourceFeatureDir\tfidf_vectorizer.pkl") {
        Copy-Item "$sourceFeatureDir\tfidf_vectorizer.pkl" "$targetFeatureDir\tfidf_vectorizer.pkl" -Force
    }
}

if (-not $SkipTraining) {
    Run-Step -Name "Model Training" -Command ".\venv\Scripts\python.exe scripts/run_training.py"
}

Write-Host "Pipeline completed successfully."
