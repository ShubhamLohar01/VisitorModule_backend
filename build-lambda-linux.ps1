# ============================================================================
# Build Lambda Deployment Package with Linux Dependencies
# This script creates a deployment-ready zip file for AWS Lambda
# ============================================================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Building Lambda Deployment Package (Linux)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$OUTPUT_ZIP = "lambda-deployment-linux.zip"
$TEMP_DIR = "lambda-build-temp"
$PYTHON_VERSION = "python3.11"

# Step 1: Clean up previous builds
Write-Host "[1/6] Cleaning up previous builds..." -ForegroundColor Yellow
if (Test-Path $TEMP_DIR) {
    Remove-Item -Recurse -Force $TEMP_DIR
}
if (Test-Path $OUTPUT_ZIP) {
    Remove-Item -Force $OUTPUT_ZIP
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null
Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# Step 2: Copy application code
Write-Host "[2/6] Copying application code..." -ForegroundColor Yellow

# Copy app directory
Copy-Item -Recurse -Path "app" -Destination "$TEMP_DIR/app"

# Copy lambda handler
Copy-Item -Path "lambda_handler.py" -Destination "$TEMP_DIR/"

# Copy requirements file
Copy-Item -Path "requirements.txt" -Destination "$TEMP_DIR/"

Write-Host "✓ Application code copied" -ForegroundColor Green
Write-Host ""

# Step 3: Install dependencies using Docker (Linux environment)
Write-Host "[3/6] Installing Python dependencies for Linux (using Docker)..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

# Check if Docker is available
try {
    docker --version | Out-Null
    $dockerAvailable = $true
} catch {
    $dockerAvailable = $false
}

if ($dockerAvailable) {
    Write-Host "Using Docker to build Linux-compatible dependencies..." -ForegroundColor Cyan
    
    # Create a temporary Dockerfile
    $dockerfileContent = @"
FROM public.ecr.aws/lambda/python:3.11

WORKDIR /build

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt -t /build/python-packages

# Clean up unnecessary files
RUN find /build/python-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
RUN find /build/python-packages -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
RUN find /build/python-packages -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
RUN find /build/python-packages -type f -name "*.pyc" -delete 2>/dev/null || true
RUN find /build/python-packages -type f -name "*.pyo" -delete 2>/dev/null || true
"@
    
    Set-Content -Path "$TEMP_DIR/Dockerfile.build" -Value $dockerfileContent
    
    # Build the Docker image
    docker build -t lambda-builder -f "$TEMP_DIR/Dockerfile.build" $TEMP_DIR
    
    # Extract dependencies
    docker create --name lambda-builder-container lambda-builder
    docker cp lambda-builder-container:/build/python-packages "$TEMP_DIR/"
    docker rm lambda-builder-container
    
    # Move packages to root
    Get-ChildItem "$TEMP_DIR/python-packages" | Move-Item -Destination $TEMP_DIR
    Remove-Item "$TEMP_DIR/python-packages" -Force
    
    Write-Host "✓ Dependencies installed using Docker" -ForegroundColor Green
} else {
    Write-Host "⚠ Docker not available. Installing with pip (may not be fully Linux-compatible)..." -ForegroundColor Yellow
    Write-Host "For production, please use Docker to ensure Linux compatibility." -ForegroundColor Yellow
    
    # Fallback to pip install
    python -m pip install -r "$TEMP_DIR/requirements.txt" -t $TEMP_DIR --upgrade --platform manylinux2014_x86_64 --only-binary=:all: 2>&1 | Out-Null
    
    Write-Host "✓ Dependencies installed (fallback method)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Clean up unnecessary files
Write-Host "[4/6] Cleaning up unnecessary files..." -ForegroundColor Yellow

# Remove __pycache__ directories
Get-ChildItem -Path $TEMP_DIR -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Remove .pyc and .pyo files
Get-ChildItem -Path $TEMP_DIR -Recurse -File -Include "*.pyc", "*.pyo" | Remove-Item -Force

# Remove dist-info and egg-info directories (but keep version info we might need)
Get-ChildItem -Path $TEMP_DIR -Recurse -Directory | Where-Object { 
    $_.Name -like "*.egg-info" -or $_.Name -like "*.dist-info" 
} | ForEach-Object {
    # Keep only METADATA and top_level.txt if they exist
    $metadataFile = Join-Path $_.FullName "METADATA"
    $topLevelFile = Join-Path $_.FullName "top_level.txt"
    
    if (Test-Path $metadataFile) {
        Get-ChildItem $_.FullName | Where-Object { 
            $_.Name -ne "METADATA" -and $_.Name -ne "top_level.txt" 
        } | Remove-Item -Recurse -Force
    } else {
        Remove-Item -Recurse -Force $_.FullName
    }
}

# Remove test directories
Get-ChildItem -Path $TEMP_DIR -Recurse -Directory -Filter "tests" | Remove-Item -Recurse -Force
Get-ChildItem -Path $TEMP_DIR -Recurse -Directory -Filter "test" | Remove-Item -Recurse -Force

Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# Step 5: Create deployment package
Write-Host "[5/6] Creating deployment package..." -ForegroundColor Yellow

# Change to temp directory and create zip
Push-Location $TEMP_DIR
try {
    # Use PowerShell Compress-Archive
    Get-ChildItem -Path . -Recurse | Compress-Archive -DestinationPath "..\$OUTPUT_ZIP" -Force
} finally {
    Pop-Location
}

Write-Host "✓ Package created: $OUTPUT_ZIP" -ForegroundColor Green
Write-Host ""

# Step 6: Display package information
Write-Host "[6/6] Package Information" -ForegroundColor Yellow
$zipSize = (Get-Item $OUTPUT_ZIP).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)

Write-Host "File: $OUTPUT_ZIP" -ForegroundColor White
Write-Host "Size: $zipSizeMB MB" -ForegroundColor White

if ($zipSizeMB -gt 50) {
    Write-Host "⚠ Warning: Package size exceeds 50MB" -ForegroundColor Yellow
    Write-Host "  Consider using Lambda Layers for dependencies" -ForegroundColor Yellow
} elseif ($zipSizeMB -gt 250) {
    Write-Host "❌ Error: Package size exceeds Lambda limit (250MB)" -ForegroundColor Red
    Write-Host "  You MUST use Lambda Layers for dependencies" -ForegroundColor Red
} else {
    Write-Host "✓ Package size is within Lambda limits" -ForegroundColor Green
}

Write-Host ""
Write-Host "Contents:" -ForegroundColor White
Get-ChildItem $TEMP_DIR -Directory | Select-Object -First 10 | ForEach-Object {
    Write-Host "  - $($_.Name)/" -ForegroundColor Gray
}
Write-Host "  - lambda_handler.py" -ForegroundColor Gray
Write-Host ""

# Cleanup temp directory
Write-Host "Cleaning up temporary files..." -ForegroundColor Gray
Remove-Item -Recurse -Force $TEMP_DIR

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Upload $OUTPUT_ZIP to AWS Lambda" -ForegroundColor White
Write-Host "2. Set handler to: lambda_handler.lambda_handler" -ForegroundColor White
Write-Host "3. Set runtime to: Python 3.11" -ForegroundColor White
Write-Host "4. Configure environment variables" -ForegroundColor White
Write-Host ""
