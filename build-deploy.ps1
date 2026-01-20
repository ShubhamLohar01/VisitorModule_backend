Write-Host "========================================"
Write-Host "Building Lambda Deployment ZIP"
Write-Host "========================================"

$PKG = "lambda-complete-final"
$ZIP = "lambda-deployment-complete.zip"

Write-Host "`n[1/4] Cleaning..."
Remove-Item -Path $PKG -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $ZIP -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $PKG | Out-Null

Write-Host "[2/4] Installing dependencies for Linux..."
pip install --platform manylinux2014_x86_64 --target=$PKG --implementation cp --python-version 3.11 --only-binary=:all: --upgrade --no-cache-dir -r complete-lambda-requirements.txt

Write-Host "`n[3/4] Copying code..."
Copy-Item -Path "lambda_handler.py" -Destination $PKG
Copy-Item -Path "app" -Destination "$PKG/app" -Recurse -ErrorAction SilentlyContinue

Write-Host "[4/4] Creating ZIP..."
Push-Location $PKG
Compress-Archive -Path * -DestinationPath "..\$ZIP" -Force
Pop-Location

$size = [math]::Round((Get-Item $ZIP).Length / 1MB, 2)
Write-Host "`nSUCCESS! Package: $ZIP ($size MB)"
