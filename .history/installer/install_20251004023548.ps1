# Windows Installer Entry Point
# Purpose: Bootstrap a minimal Python virtualenv for the installer runtime and invoke the TUI wizard.
# Safe-by-default: Does not install system-wide software; confines changes to repo directory.

param(
  [switch]$NoBrowserInstall = $false,
  [switch]$SkipPlaywright = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Push-Location $repoRoot

function Write-Info($msg) { Write-Host "[Installer] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[Installer] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[Installer] $msg" -ForegroundColor Red }

# 1) Ensure Python is present
try {
  $pyver = & python -V 2>$null
  if (-not $pyver) { throw "python not found on PATH" }
  Write-Info "Detected $pyver"
} catch {
  Write-Warn "Python not found. Please install Python 3.13 and re-run."
  Write-Warn "Download: https://www.python.org/downloads/windows/"
  exit 1
}

# 2) Create .venv for installer runtime
$venvPath = Join-Path $repoRoot ".venv"
if (-not (Test-Path $venvPath)) {
  Write-Info "Creating virtual environment (.venv)"
  & python -m venv .venv
}

# 3) Activate venv and install installer deps
$activate = Join-Path $venvPath "Scripts/Activate.ps1"
. $activate
Write-Info "Installing installer dependencies"
python -m pip install --upgrade pip | Out-Null
python -m pip install -r installer/requirements_installer.txt

# 4) Launch TUI wizard
if ($SkipPlaywright) { $env:INSTALLER_SKIP_PLAYWRIGHT = '1' } else { $env:INSTALLER_SKIP_PLAYWRIGHT = '0' }
python installer/setup_wizard.py

if ($LASTEXITCODE -ne 0) {
  Write-Err "Installer wizard exited with code $LASTEXITCODE"
  exit $LASTEXITCODE
}

Write-Info "Installer completed successfully."
Pop-Location

