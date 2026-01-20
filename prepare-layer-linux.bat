@echo off
REM Script to prepare Lambda Layer with Linux-compatible dependencies
REM This installs packages for Linux platform (required for Lambda)

setlocal enabledelayedexpansion

echo === Preparing Lambda Layer (Linux-compatible) ===
echo.
echo IMPORTANT: This will install Linux-compatible packages
echo This may take longer and requires internet connection
echo.

REM Clean previous builds
if exist lambda-layer rmdir /s /q lambda-layer
if exist layer.zip del /q layer.zip

REM Create folder structure
echo Creating folder structure...
mkdir lambda-layer
mkdir lambda-layer\python

REM Install dependencies for Linux
echo.
echo Installing dependencies for Linux (manylinux2014_x86_64)...
echo This may take 5-10 minutes...
echo.

cd lambda-layer\python

REM Try to install with Linux platform flags
pip install -r ..\..\requirements.txt -t . --platform manylinux2014_x86_64 --implementation cp --python-version 3.11 --only-binary=:all: --upgrade --no-deps

REM If that fails, install without platform flags (will work but may have issues)
if errorlevel 1 (
    echo.
    echo Platform-specific install failed, trying standard install...
    echo WARNING: This may not work correctly in Lambda
    pip install -r ..\..\requirements.txt -t . --upgrade
)

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo.
    echo SOLUTION: Use Docker method instead (see prepare-layer-docker.bat)
    echo OR: Build the layer on a Linux machine
    cd ..\..
    exit /b 1
)

cd ..\..

REM Create ZIP file
echo.
echo Creating ZIP file...
cd lambda-layer
powershell -Command "Compress-Archive -Path python -DestinationPath ..\layer.zip -Force"
cd ..

if not exist layer.zip (
    echo ERROR: Failed to create ZIP file
    exit /b 1
)

REM Get file size
for %%A in (layer.zip) do set SIZE=%%~zA
set /a SIZE_MB=%SIZE% / 1048576

echo.
echo === Layer Prepared! ===
echo.
echo File: layer.zip
echo Size: %SIZE_MB% MB
echo.
echo NOTE: If you still get pydantic_core errors, use Docker method instead
echo.
echo Next steps:
echo   1. Delete old layer in AWS (if exists)
echo   2. Create new layer with this layer.zip
echo   3. Attach to Lambda function
echo.

endlocal
