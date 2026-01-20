@echo off
REM Build Lambda Layer Script for Windows
REM This script creates a Lambda Layer with all Python dependencies

setlocal enabledelayedexpansion

set LAYER_NAME=visitor-management-dependencies
set PYTHON_VERSION=python3.11
set LAYER_DIR=layer
set BUILD_DIR=build

echo === Building Lambda Layer ===
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist %LAYER_DIR% rmdir /s /q %LAYER_DIR%
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%
mkdir %LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages
mkdir %BUILD_DIR%

REM Install dependencies into layer directory
echo Installing dependencies into layer...
pip install -r layer-requirements.txt ^
    --target %LAYER_DIR%\%PYTHON_VERSION%\lib\python3.11\site-packages ^
    --platform manylinux2014_x86_64 ^
    --implementation cp ^
    --python-version 3.11 ^
    --only-binary=:all: ^
    --upgrade ^
    --no-cache-dir

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

REM Create zip file
echo Creating layer zip file...
cd %LAYER_DIR%
powershell -Command "Compress-Archive -Path * -DestinationPath ..\%BUILD_DIR%\%LAYER_NAME%.zip -Force"
cd ..

echo.
echo === Layer Build Complete ===
echo Layer file: %BUILD_DIR%\%LAYER_NAME%.zip
echo Next step: Deploy the layer using deploy-layer.bat

endlocal
