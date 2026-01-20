@echo off
REM Batch script to create Lambda Layer on Windows
REM This downloads Linux-compatible wheels and creates the layer ZIP

echo Creating Lambda Layer for Python 3.11...

REM Create folder structure
if not exist "lambda-layer\python\lib\python3.11\site-packages" (
    mkdir "lambda-layer\python\lib\python3.11\site-packages"
)

cd lambda-layer\python\lib\python3.11\site-packages

echo Downloading Linux-compatible dependencies...
echo This will take 5-10 minutes...

REM Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies with Linux platform flag
python -m pip install --platform manylinux2014_x86_64 --target . --only-binary :all: --no-cache-dir --python-version 3.11 --implementation cp --abi cp311 -r ..\..\..\..\..\requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    cd ..\..\..\..\..
    exit /b 1
)

echo Cleaning up unnecessary files...

REM Remove __pycache__ directories (PowerShell needed for this)
powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"

REM Remove .pyc files
powershell -Command "Get-ChildItem -Path . -Recurse -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"

echo Creating ZIP file...
cd ..\..\..\..\..\..

REM Create ZIP using PowerShell
powershell -Command "Compress-Archive -Path lambda-layer\python -DestinationPath layer.zip -Force"

REM Check file size
if exist layer.zip (
    for %%A in (layer.zip) do (
        set size=%%~zA
    )
    echo.
    echo Layer created successfully!
    echo File: layer.zip
    echo.
    echo You can upload this to AWS Lambda Layers!
) else (
    echo Error: Failed to create ZIP file
    exit /b 1
)

echo.
echo Done! Your layer.zip is ready to upload to AWS Lambda.
