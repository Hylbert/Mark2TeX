Write-Host "Checking Mark2TeX dependencies for Windows..." -ForegroundColor Cyan

# 1. Privilege Check
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Please run this script as Administrator!" -ForegroundColor Red
    exit 1
}

# 2. Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✓ Docker is already installed." -ForegroundColor Green
} else {
    Write-Host "Installing Docker Desktop via winget..."
    winget install Docker.DockerDesktop --silent --accept-package-agreements --accept-source-agreements
    Write-Host "✓ Docker installed successfully." -ForegroundColor Green
}

# 3. Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✓ Python is already installed." -ForegroundColor Green
} else {
    Write-Host "Installing Python via winget..."
    winget install Python.Python.3 --silent --accept-package-agreements --accept-source-agreements
    Write-Host "✓ Python installed successfully." -ForegroundColor Green
}

# 4. Final Validation
docker --version
python --version

Write-Host "`nPost-installation step:" -ForegroundColor Cyan
Write-Host "If this is your first time installing Docker, please restart your computer to activate WSL2."
