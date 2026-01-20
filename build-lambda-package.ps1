# Lambda Deployment Package Builder with Linux Dependencies
# This script creates a proper Lambda deployment package with Linux-compatible dependencies

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Lambda Deployment Package Builder" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Set error action
$ErrorActionPreference = "Stop"

# Configuration
$PACKAGE_DIR = "lambda-deployment-package"
$OUTPUT_ZIP = "lambda-deployment.zip"
$PYTHON_VERSION = "3.9"

# Clean previous build
Write-Host "Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path $PACKAGE_DIR) {
    Remove-Item -Path $PACKAGE_DIR -Recurse -Force
}
if (Test-Path $OUTPUT_ZIP) {
    Remove-Item -Path $OUTPUT_ZIP -Force
}

# Create package directory
Write-Host "Creating package directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $PACKAGE_DIR | Out-Null

# Check if Docker is available
Write-Host "Checking Docker availability..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    $useDocker = $true
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    $useDocker = $false
    Write-Host "Docker not found. Will use pip with --platform flag." -ForegroundColor Yellow
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow

if ($useDocker) {
    # Use Docker to install Linux-compatible dependencies
    Write-Host "Using Docker to build Linux-compatible dependencies..." -ForegroundColor Cyan
    
    $dockerCommand = @"
docker run --rm -v `"${PWD}:/var/task`" public.ecr.aws/lambda/python:$PYTHON_VERSION bash -c `"
    pip install --target /var/task/$PACKAGE_DIR -r /var/task/complete-lambda-requirements.txt --no-cache-dir &&
    echo 'Dependencies installed successfully'
`"
"@
    
    Invoke-Expression $dockerCommand
    
} else {
    # Use pip with platform-specific flags
    Write-Host "Using pip with Linux platform flags..." -ForegroundColor Cyan
    
    pip install `
        --platform manylinux2014_x86_64 `
        --target=$PACKAGE_DIR `
        --implementation cp `
        --python-version $PYTHON_VERSION `
        --only-binary=:all: `
        --upgrade `
        -r complete-lambda-requirements.txt
}

# Copy application code
Write-Host ""
Write-Host "Copying application code..." -ForegroundColor Yellow

# Copy main Lambda handler
Copy-Item -Path "lambda_handler.py" -Destination $PACKAGE_DIR

# Copy app directory if it exists
if (Test-Path "app") {
    Write-Host "Copying app directory..." -ForegroundColor Yellow
    Copy-Item -Path "app" -Destination "$PACKAGE_DIR/app" -Recurse
}

# Clean up unnecessary files
Write-Host ""
Write-Host "Cleaning up unnecessary files..." -ForegroundColor Yellow

$cleanupPatterns = @(
    "*.pyc",
    "__pycache__",
    "*.dist-info",
    "*.egg-info",
    ".pytest_cache",
    "tests",
    "test",
    "*.so.dSYM"
)

foreach ($pattern in $cleanupPatterns) {
    Get-ChildItem -Path $PACKAGE_DIR -Recurse -Filter $pattern -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

# Remove large unnecessary packages
$unnecessaryDirs = @(
    "boto3",
    "botocore",
    "s3transfer",
    "pip",
    "setuptools",
    "wheel"
)

foreach ($dir in $unnecessaryDirs) {
    $dirPath = Join-Path $PACKAGE_DIR $dir
    if (Test-Path $dirPath) {
        Write-Host "Removing $dir (available in Lambda runtime)..." -ForegroundColor Gray
        Remove-Item -Path $dirPath -Recurse -Force
    }
}

# Create ZIP file
Write-Host ""
Write-Host "Creating ZIP file..." -ForegroundColor Yellow

# Change to package directory
Push-Location $PACKAGE_DIR

# Create zip using PowerShell's Compress-Archive
$files = Get-ChildItem -Recurse
Write-Host "Compressing $($files.Count) items..." -ForegroundColor Gray

# Use System.IO.Compression for better compatibility
Add-Type -Assembly System.IO.Compression.FileSystem
$compressionLevel = [System.IO.Compression.CompressionLevel]::Optimal
$zipPath = Join-Path $PWD.Path "..\$OUTPUT_ZIP"
[System.IO.Compression.ZipFile]::CreateFromDirectory($PWD.Path, $zipPath, $compressionLevel, $false)

Pop-Location

# Get file size
$zipSize = (Get-Item $OUTPUT_ZIP).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Deployment Package Created Successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package: $OUTPUT_ZIP" -ForegroundColor Cyan
Write-Host "Size: $zipSizeMB MB" -ForegroundColor Cyan
Write-Host ""

if ($zipSizeMB -gt 50) {
    Write-Host "WARNING: Package size exceeds 50MB limit for direct Lambda upload!" -ForegroundColor Red
    Write-Host "You'll need to upload to S3 and deploy from there." -ForegroundColor Yellow
} else {
    Write-Host "You can upload this directly to Lambda via AWS Console or CLI." -ForegroundColor Green
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Upload $OUTPUT_ZIP to your Lambda function" -ForegroundColor White
Write-Host "2. Set handler to: lambda_handler.lambda_handler" -ForegroundColor White
Write-Host "3. Set runtime to: python$PYTHON_VERSION" -ForegroundColor White
Write-Host ""
