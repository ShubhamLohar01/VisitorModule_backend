@echo off
REM ========================================
REM Complete Lambda Deployment Package Builder
REM Includes Backend Code + All Dependencies
REM ========================================

echo ========================================
echo COMPLETE Lambda Deployment Package Builder
echo ========================================

REM [1/6] Clean previous builds
echo [1/6] Cleaning previous builds...
if exist "deployment-package" rmdir /s /q "deployment-package"
if exist "visitor-backend-complete.zip" del "visitor-backend-complete.zip"

REM [2/6] Create deployment package directory
echo [2/6] Creating deployment package structure...
mkdir "deployment-package"

REM [3/6] Install dependencies directly into deployment package
echo [3/6] Installing dependencies with Linux compatibility...
echo Target: AWS Lambda Python 3.11 (Linux x86_64)

pip install -r complete-lambda-requirements.txt ^
    --target "deployment-package" ^
    --platform manylinux2014_x86_64 ^
    --implementation cp ^
    --python-version 3.11 ^
    --only-binary=:all: ^
    --upgrade

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM [4/6] Copy backend application code
echo [4/6] Copying backend application code...

REM Copy main handler
copy "lambda_handler.py" "deployment-package\"
copy "debug_lambda_handler.py" "deployment-package\" 2>nul

REM Copy FastAPI app directory
xcopy "app" "deployment-package\app\" /E /I /H /Y
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to copy app directory
    pause
    exit /b 1
)

REM Copy configuration files if they exist
copy ".env" "deployment-package\" 2>nul
copy "pyproject.toml" "deployment-package\" 2>nul

REM [5/6] Verify critical modules
echo [5/6] Verifying critical modules...
python -c "
import os
import sys
sys.path.insert(0, 'deployment-package')

try:
    import mangum
    print('✅ mangum - FOUND')
    print(f'   Version: {mangum.__version__}')
except ImportError as e:
    print(f'❌ mangum - NOT FOUND: {e}')

try:
    import fastapi
    print('✅ fastapi - FOUND') 
    print(f'   Version: {fastapi.__version__}')
except ImportError as e:
    print(f'❌ fastapi - NOT FOUND: {e}')

try:
    import boto3
    print('✅ boto3 - FOUND')
    print(f'   Version: {boto3.__version__}')
except ImportError as e:
    print(f'❌ boto3 - NOT FOUND: {e}')

try:
    sys.path.insert(0, 'deployment-package')
    from app.main import app
    print('✅ app.main - FOUND')
    print(f'   App type: {type(app)}')
except ImportError as e:
    print(f'❌ app.main - NOT FOUND: {e}')
"

REM [6/6] Create deployment zip
echo [6/6] Creating deployment zip package...

REM Change to deployment-package directory and zip contents
cd deployment-package
powershell -Command "Compress-Archive -Path * -DestinationPath ..\visitor-backend-complete.zip -Force"
cd ..

REM Check final size
for %%I in ("visitor-backend-complete.zip") do set "filesize=%%~zI"
set /a "filesizeMB=%filesize% / 1048576"

echo.
echo ========================================
echo 🎯 DEPLOYMENT PACKAGE BUILD SUCCESSFUL
echo ========================================
echo.
echo Next Steps:
echo 1. Upload to S3: visitor-backend-complete.zip
echo 2. Create/Update Lambda function from S3
echo 3. Set handler to: lambda_handler.lambda_handler
echo 4. Set runtime to: Python 3.11
echo 5. Test function
echo.
echo Package file: visitor-backend-complete.zip
echo Size: %filesizeMB% MB (%filesize% bytes)
echo.

if %filesizeMB% GTR 250 (
    echo ⚠️  Warning: Package size is %filesizeMB% MB
    echo    Lambda limit is 250 MB unzipped
    echo    Consider removing unused dependencies
) else (
    echo ✅ Size is within Lambda limits
)

echo.
echo Ready for S3 upload and Lambda deployment!
echo ========================================

pause