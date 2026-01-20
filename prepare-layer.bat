@echo off
REM Script to prepare Lambda Layer with dependencies
REM This will install all packages and create a ZIP file ready for upload

setlocal enabledelayedexpansion

echo === Preparing Lambda Layer ===
echo.

REM Clean previous builds
if exist lambda-layer rmdir /s /q lambda-layer
if exist layer.zip del /q layer.zip

REM Create folder structure
echo Creating folder structure...
mkdir lambda-layer
mkdir lambda-layer\python

REM Install dependencies for Linux (Lambda runs on Linux)
echo.
echo Installing dependencies for Linux platform (this may take a few minutes)...
echo.

cd lambda-layer\python
pip install -r ..\..\requirements.txt -t . --platform manylinux2014_x86_64 --implementation cp --python-version 3.11 --only-binary=:all: --upgrade

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check:
    echo   1. Python 3.11 is installed
    echo   2. pip is working correctly
    echo   3. You have internet connection
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
echo === Layer Prepared Successfully! ===
echo.
echo File: layer.zip
echo Size: %SIZE_MB% MB
echo.
echo Next steps:
echo   1. Go to AWS Lambda Console
echo   2. Click "Layers" in left sidebar
echo   3. Click "Create layer"
echo   4. Upload layer.zip
echo   5. Select Python 3.11 as compatible runtime
echo   6. Attach the layer to your Lambda function
echo.
echo Location: %CD%\layer.zip
echo.

endlocal
