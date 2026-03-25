# install_packages.ps1
Write-Host "Installing Python packages..." -ForegroundColor Cyan

# Try to find Python
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    $pythonPath = (Get-Command py -ErrorAction SilentlyContinue).Source
}

if (-not $pythonPath) {
    Write-Host "Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $pythonPath" -ForegroundColor Green

# Ensure pip is installed
Write-Host "Checking pip..." -ForegroundColor Yellow
& $pythonPath -m ensurepip --upgrade

# Install packages
Write-Host "Installing aiohttp..." -ForegroundColor Yellow
& $pythonPath -m pip install aiohttp python-dotenv

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
& $pythonPath -c "import aiohttp; print('✓ aiohttp installed')"
& $pythonPath -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"

Write-Host "Done!" -ForegroundColor Green