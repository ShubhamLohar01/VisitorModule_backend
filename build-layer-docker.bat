@echo off
REM Build Lambda Layer using Docker (Linux-compatible)
REM This ensures packages are compiled for Linux, not Windows

setlocal enabledelayedexpansion

echo ========================================
echo Building Lambda Layer with Docker
echo ========================================
echo.
echo This will create Linux-compatible packages for AWS Lambda
echo.

REM Check if Docker is running
echo Checking Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Docker is not running!
    echo.
    echo Please do the following:
    echo   1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
    echo   2. Start Docker Desktop
    echo   3. Wait for Docker to be running (green icon in system tray)
    echo   4. Run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist layer.zip del /q layer.zip
if exist lambda-layer rmdir /s /q lambda-layer
echo [OK] Cleaned
echo.

REM Build Docker image
echo ========================================
echo Step 1: Building Docker image...
echo ========================================
echo This may take 5-10 minutes on first run...
echo.

docker build -t lambda-layer-builder -f Dockerfile.layer .

if errorlevel 1 (
    echo.
    echo [ERROR] Docker build failed!
    echo.
    echo Please check:
    echo   - Docker is running
    echo   - Dockerfile.layer exists
    echo   - requirements.txt exists
    echo   - You have internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Docker image built successfully
echo.

REM Run container to create layer.zip
echo ========================================
echo Step 2: Creating layer ZIP file...
echo ========================================
echo.

docker run --rm -v "%CD%":/output lambda-layer-builder sh -c "cp /layer.zip /output/layer.zip"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create layer.zip
    echo.
    pause
    exit /b 1
)

REM Check if layer.zip was created
if not exist layer.zip (
    echo.
    echo [ERROR] layer.zip was not created
    echo.
    echo Trying alternative method...
    docker run --rm lambda-layer-builder cat /layer.zip > layer.zip
    
    if not exist layer.zip (
        echo [ERROR] Alternative method also failed
        pause
        exit /b 1
    )
)

REM Get file size
for %%A in (layer.zip) do set SIZE=%%~zA
set /a SIZE_MB=%SIZE% / 1048576

echo.
echo ========================================
echo Layer Built Successfully!
echo ========================================
echo.
echo File: layer.zip
echo Size: %SIZE_MB% MB
echo Location: %CD%\layer.zip
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Go to AWS Lambda Console
echo 2. Click "Layers" in left sidebar
echo 3. Click "Create layer"
echo 4. Name: visitor-management-dependencies
echo 5. Upload: layer.zip
echo 6. Compatible runtime: Python 3.11
echo 7. Click "Create"
echo.
echo 8. Go to your Lambda function
echo 9. Scroll to "Layers" section
echo 10. Click "Add a layer"
echo 11. Select your new layer
echo 12. Click "Add"
echo.
echo 13. Test your Lambda function again
echo.
echo ========================================
echo.

endlocal
