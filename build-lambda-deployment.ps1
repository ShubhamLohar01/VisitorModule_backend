# AWS Lambda Deployment Package Builder
# Creates a deployment package with Linux-compatible dependencies for AWS Lambda
# Python 3.11 Runtime - Amazon Linux 2

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AWS Lambda Deployment Package Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PYTHON_VERSION = "3.11"
$PLATFORM = "manylinux2014_x86_64"
$PACKAGE_DIR = "lambda-deployment-package"
$OUTPUT_ZIP = "lambda-deployment-package.zip"

# Clean up previous builds
Write-Host "[1/5] Cleaning up previous builds..." -ForegroundColor Yellow
if (Test-Path $PACKAGE_DIR) {
    Remove-Item -Recurse -Force $PACKAGE_DIR
    Write-Host "  Removed old package directory" -ForegroundColor Green
}
if (Test-Path $OUTPUT_ZIP) {
    Remove-Item -Force $OUTPUT_ZIP
    Write-Host "  Removed old zip file" -ForegroundColor Green
}

# Create package directory
Write-Host ""
Write-Host "[2/5] Creating package directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $PACKAGE_DIR | Out-Null
Write-Host "  Created: $PACKAGE_DIR" -ForegroundColor Green

# Install dependencies for Linux
Write-Host ""
Write-Host "[3/5] Installing Linux-compatible dependencies..." -ForegroundColor Yellow
Write-Host "  This may take several minutes..." -ForegroundColor Gray

$pipArgs = @(
    "install",
    "-r", "complete-lambda-requirements.txt",
    "-t", $PACKAGE_DIR,
    "--platform", $PLATFORM,
    "--python-version", $PYTHON_VERSION,
    "--only-binary=:all:",
    "--upgrade",
    "--no-cache-dir"
)

try {
    & pip $pipArgs
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed with exit code $LASTEXITCODE"
    }
    Write-Host "  Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "  Failed to install dependencies" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Copy application code
Write-Host ""
Write-Host "[4/5] Copying application code..." -ForegroundColor Yellow

# Copy the app directory
Write-Host "  Copying app directory..." -ForegroundColor Gray
Copy-Item -Path "app" -Destination "$PACKAGE_DIR\app" -Recurse -Force
Write-Host "  Copied app/" -ForegroundColor Green

# Copy lambda handler
Write-Host "  Copying lambda_handler.py..." -ForegroundColor Gray
Copy-Item -Path "lambda_handler.py" -Destination "$PACKAGE_DIR\lambda_handler.py" -Force
Write-Host "  Copied lambda_handler.py" -ForegroundColor Green

# Create .env file for Lambda (if needed)
if (Test-Path ".env") {
    Write-Host "  Copying .env file..." -ForegroundColor Gray
    Copy-Item -Path ".env" -Destination "$PACKAGE_DIR\.env" -Force
    Write-Host "  Copied .env" -ForegroundColor Green
}

# Clean up unnecessary files
Write-Host ""
Write-Host "  Cleaning up unnecessary files..." -ForegroundColor Gray
$cleanupPatterns = @(
    "$PACKAGE_DIR\**\*.pyc",
    "$PACKAGE_DIR\**\*.pyo",
    "$PACKAGE_DIR\**\*.pyd",
    "$PACKAGE_DIR\**\__pycache__",
    "$PACKAGE_DIR\**\.pytest_cache",
    "$PACKAGE_DIR\**\.git",
    "$PACKAGE_DIR\**\.gitignore",
    "$PACKAGE_DIR\**\*.dist-info",
    "$PACKAGE_DIR\**\tests",
    "$PACKAGE_DIR\**\test"
)

foreach ($pattern in $cleanupPatterns) {
    if (Test-Path $pattern) {
        Remove-Item -Path $pattern -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "  Cleaned up cache and test files" -ForegroundColor Green

# Create ZIP file
Write-Host ""
Write-Host "[5/5] Creating deployment ZIP file..." -ForegroundColor Yellow
Write-Host "  Compressing package (this may take a while)..." -ForegroundColor Gray

try {
    # Use PowerShell's Compress-Archive
    Compress-Archive -Path "$PACKAGE_DIR\*" -DestinationPath $OUTPUT_ZIP -Force
    
    $zipSize = (Get-Item $OUTPUT_ZIP).Length / 1MB
    Write-Host "  Created: $OUTPUT_ZIP" -ForegroundColor Green
    Write-Host "  Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Green
} catch {
    Write-Host "  Failed to create ZIP file" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Verify package contents
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Package Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Package Contents:" -ForegroundColor Yellow
Write-Host "  Application code (app/)" -ForegroundColor Green
Write-Host "  Lambda handler (lambda_handler.py)" -ForegroundColor Green
Write-Host "  Python dependencies (Linux compatible)" -ForegroundColor Green

Write-Host ""
Write-Host "Deployment File:" -ForegroundColor Yellow
Write-Host "  $OUTPUT_ZIP" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Upload $OUTPUT_ZIP to AWS Lambda" -ForegroundColor White
Write-Host "  2. Set handler to: lambda_handler.lambda_handler" -ForegroundColor White
Write-Host "  3. Set runtime to: Python $PYTHON_VERSION" -ForegroundColor White
Write-Host "  4. Configure environment variables in Lambda" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Optional: Check if file size exceeds Lambda limit
if ($zipSize -gt 50) {
    Write-Host "WARNING: Package size exceeds 50MB" -ForegroundColor Yellow
    Write-Host "Consider using Lambda Layers for dependencies" -ForegroundColor Yellow
    Write-Host ""
}
