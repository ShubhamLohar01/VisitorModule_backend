@echo off
REM Complete Lambda Dependencies Layer Builder
REM Builds ALL dependencies for AWS Lambda Linux environment
REM Ensures 100% compatibility with Python 3.11 on AWS Lambda

setlocal enabledelayedexpansion 

set LAYER_NAME=complete-visitor-dependencies
set PYTHON_VERSION=python3.11
set LAYER_DIR=complete-lambda-layer
set BUILD_DIR=lambda-build

echo ========================================
echo COMPLETE Lambda Dependencies Builder
echo ========================================
echo.

REM Clean previous builds
echo [1/5] Cleaning previous builds...
if exist %LAYER_DIR% rmdir /s /q %LAYER_DIR%
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%
mkdir %LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages
mkdir %BUILD_DIR%

echo [2/5] Installing dependencies with Linux compatibility...
echo Target: AWS Lambda Python 3.11 (Linux x86_64)
echo.

pip install -r complete-lambda-requirements.txt ^
    --target %LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages ^
    --platform manylinux2014_x86_64 ^
    --implementation cp ^
    --python-version 3.11 ^
    --only-binary=:all: ^
    --upgrade ^
    --no-cache-dir ^
    --force-reinstall

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo [3/5] Verifying critical modules...

REM Check if mangum is installed
if exist "%LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages\mangum" (
    echo ✅ mangum - FOUND
) else (
    echo ❌ mangum - MISSING
    echo ERROR: Critical dependency missing
    exit /b 1
)

REM Check if fastapi is installed
if exist "%LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages\fastapi" (
    echo ✅ fastapi - FOUND
) else (
    echo ❌ fastapi - MISSING
    echo ERROR: Critical dependency missing
    exit /b 1
)

REM Check if boto3 is installed
if exist "%LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages\boto3" (
    echo ✅ boto3 - FOUND
) else (
    echo ❌ boto3 - MISSING
    echo ERROR: Critical dependency missing
    exit /b 1
)

REM Check if twilio is installed
if exist "%LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages\twilio" (
    echo ✅ twilio - FOUND
) else (
    echo ❌ twilio - MISSING
    echo ERROR: Critical dependency missing
    exit /b 1
)

echo.
echo [4/5] Creating optimized Lambda layer zip...
cd %LAYER_DIR%
powershell -Command "Compress-Archive -Path * -DestinationPath ..\%BUILD_DIR%\%LAYER_NAME%.zip -Force -CompressionLevel Optimal"
cd ..

echo.
echo [5/5] Validating final package...

REM Get file size
for /f %%i in ('powershell -command "(Get-Item '%BUILD_DIR%\%LAYER_NAME%.zip').Length"') do set FILE_SIZE=%%i
set /a FILE_SIZE_MB=!FILE_SIZE!/1048576

echo File: %BUILD_DIR%\%LAYER_NAME%.zip
echo Size: !FILE_SIZE_MB! MB (!FILE_SIZE! bytes)

REM Check size limit (250MB unzipped, ~50-60MB zipped)
if !FILE_SIZE_MB! gtr 60 (
    echo WARNING: Layer size is large (!FILE_SIZE_MB! MB)
    echo Consider removing unnecessary dependencies
) else (
    echo ✅ Size is within optimal range
)

echo.
echo ========================================
echo 🎉 COMPLETE Layer Build Successful!
echo ========================================
echo.
echo Next Steps:
echo 1. Upload to AWS Lambda: %BUILD_DIR%\%LAYER_NAME%.zip
echo 2. Compatible with: Python 3.11, x86_64 architecture
echo 3. Attach to Lambda function in AWS Console
echo 4. Test function - mangum import should work!
echo.
echo Layer file: %BUILD_DIR%\%LAYER_NAME%.zip
echo Size: !FILE_SIZE_MB! MB
echo.

endlocal