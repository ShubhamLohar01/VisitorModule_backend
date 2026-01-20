# PowerShell Script to Create Lambda Layer on Windows
# This downloads Linux-compatible wheels and creates the layer ZIP

Write-Host "Creating Lambda Layer for Python 3.11..." -ForegroundColor Green

# Get the script directory (backend folder)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) {
    $scriptDir = Get-Location
}

# Create folder structure
$layerDir = Join-Path $scriptDir "lambda-layer"
$pythonPath = Join-Path $layerDir "python\lib\python3.11\site-packages"
$requirementsFile = Join-Path $scriptDir "requirements.txt"

Write-Host "Creating directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $pythonPath | Out-Null

# Change to the site-packages directory
Push-Location $pythonPath

Write-Host "Downloading Linux-compatible dependencies..." -ForegroundColor Yellow
Write-Host "This will take 5-10 minutes..." -ForegroundColor Yellow

# Verify requirements.txt exists
if (-not (Test-Path $requirementsFile)) {
    Write-Host "Error: requirements.txt not found at $requirementsFile" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install dependencies with Linux platform flag
# manylinux2014_x86_64 is compatible with Lambda's runtime
python -m pip install `
    --platform manylinux2014_x86_64 `
    --target . `
    --only-binary :all: `
    --no-cache-dir `
    --python-version 3.11 `
    --implementation cp `
    --abi cp311 `
    -r $requirementsFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Cleaning up unnecessary files..." -ForegroundColor Yellow

# Remove __pycache__ directories
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Remove .pyc files
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# Remove .pyo files
Get-ChildItem -Path . -Recurse -Filter "*.pyo" | Remove-Item -Force -ErrorAction SilentlyContinue

# Remove test directories (optional - saves space)
# BUT: Don't remove *.docs modules - they're needed at runtime!
# boto3.docs and botocore.docs are runtime modules, not just documentation!
Get-ChildItem -Path . -Recurse -Directory -Filter "tests" | Where-Object { $_.FullName -notlike "*boto*" } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Directory -Filter "test" | Where-Object { $_.FullName -notlike "*boto*" } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# IMPORTANT: Never remove *.docs modules - they may be runtime modules!
# boto3.docs and botocore.docs are imported at runtime for help/documentation features

Write-Host "Creating ZIP file..." -ForegroundColor Yellow

# Go back to original directory
Pop-Location

# Create ZIP file
$zipFile = Join-Path $scriptDir "layer.zip"
Compress-Archive -Path (Join-Path $layerDir "python") -DestinationPath $zipFile -Force
if (Test-Path $zipFile) {
    $fileSize = (Get-Item $zipFile).Length / 1MB
    Write-Host "`nLayer created successfully!" -ForegroundColor Green
    Write-Host "File: $zipFile" -ForegroundColor Green
    Write-Host "Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
    
    if ($fileSize -gt 50) {
        Write-Host "`nWarning: File is over 50 MB. You'll need to upload via S3." -ForegroundColor Yellow
        Write-Host "Upload command: aws s3 cp layer.zip s3://your-bucket-name/layer.zip" -ForegroundColor Yellow
    } else {
        Write-Host "`nYou can upload this directly to Lambda Layers!" -ForegroundColor Green
    }
} else {
    Write-Host "Error: Failed to create ZIP file" -ForegroundColor Red
    exit 1
}

Write-Host "`nDone! Your layer.zip is ready to upload to AWS Lambda." -ForegroundColor Green
