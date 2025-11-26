# GoodBoy.AI Setup Script for Windows
# This script sets up the complete development environment

Param(
    [switch]$SkipTests,
    [switch]$SkipModel
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   GoodBoy.AI - Bathy City Setup" -ForegroundColor Cyan
Write-Host "   Self-Aware, Self-Learning AI Assistant" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Move to repo root
Set-Location -Path $PSScriptRoot

Write-Host "`n[GoodBoy.AI] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[GoodBoy.AI] Found: $pythonVersion" -ForegroundColor Green
    
    # Extract version number
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "[WARNING] Python 3.8+ recommended, found $pythonVersion" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "[GoodBoy.AI] Python not found! Please install Python 3.10+ first." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment
Write-Host "`n[GoodBoy.AI] Setting up virtual environment..." -ForegroundColor Yellow
if (-Not (Test-Path "venv")) {
    Write-Host "[GoodBoy.AI] Creating virtual environment in .\venv" -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[GoodBoy.AI] venv already exists, reusing." -ForegroundColor Green
}

# Activate venv
Write-Host "[GoodBoy.AI] Activating venv" -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

Write-Host "`n[GoodBoy.AI] Installing Python dependencies from requirements.txt" -ForegroundColor Cyan
Write-Host "This may take several minutes..." -ForegroundColor Gray

# Upgrade pip first
python -m pip install --upgrade pip --quiet

# Install requirements
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install some dependencies" -ForegroundColor Red
    Write-Host "Try running: pip install -r requirements.txt manually" -ForegroundColor Yellow
    Read-Host "Press Enter to continue anyway"
}

# Create required directories
Write-Host "`n[GoodBoy.AI] Creating directory structure..." -ForegroundColor Yellow
$directories = @("data", "models", "memory", "memory/docs", "logs", "assets")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[GoodBoy.AI] Created: $dir" -ForegroundColor Green
    }
}

# Create default config if not exists
$configPath = "data/GoodBoy_config.json"
if (-Not (Test-Path $configPath)) {
    Write-Host "[GoodBoy.AI] Creating default configuration..." -ForegroundColor Yellow
    $defaultConfig = @{
        engine = "local"
        model_path = "models/"
        cloud_api_base = "http://127.0.0.1:8000"
        api_port = 8000
        max_tokens = 512
        temperature = 0.6
        user_name = "Mayor"
        theme = "dark"
        auto_start_server = $true
    } | ConvertTo-Json -Depth 10
    Set-Content -Path $configPath -Value $defaultConfig -Encoding UTF8
    Write-Host "[GoodBoy.AI] Config created at $configPath" -ForegroundColor Green
}

# Create default behavior instructions if not exists
$behaviorPath = "data/Behavior_instructions.json"
if (-Not (Test-Path $behaviorPath)) {
    Write-Host "[GoodBoy.AI] Creating default behavior instructions..." -ForegroundColor Yellow
    $defaultBehavior = @{
        system_prompt = "You are GoodBoy.AI: loyal, concise, and efficient. Use uploaded context first; do NOT repeat the user's words back. If info is missing, say what you need, then give next steps."
    } | ConvertTo-Json -Depth 10
    Set-Content -Path $behaviorPath -Value $defaultBehavior -Encoding UTF8
}

$chatsPath = "data/chats_content.json"
if (-Not (Test-Path $chatsPath)) {
    Set-Content -Path $chatsPath -Value "[]" -Encoding UTF8
}

# Run tests unless skipped
if (-Not $SkipTests) {
    Write-Host "`n[GoodBoy.AI] Running pytest to verify installation" -ForegroundColor Cyan
    pytest tests/ -v --tb=short 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[GoodBoy.AI] Some tests failed, but setup continues." -ForegroundColor Yellow
    }
} else {
    Write-Host "[GoodBoy.AI] Skipping tests as requested." -ForegroundColor Yellow
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   GoodBoy.AI Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Download a GGUF model (optional - use Model Manager in UI)" -ForegroundColor White
Write-Host "     Recommended: Qwen2.5-7B-Instruct or Phi-3-Mini" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Launch GoodBoy.AI:" -ForegroundColor White
Write-Host "     > .\GoodBoy_launcher.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Or run components separately:" -ForegroundColor Yellow
Write-Host "     Server:    .\run_server.bat" -ForegroundColor White
Write-Host "     Dashboard: .\run_dashboard.bat" -ForegroundColor White
Write-Host ""
Write-Host "GoodBoy.AI is ready to serve!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
