@echo off
REM Deploy Lambda Layer Script for Windows
REM This script uploads the layer to AWS Lambda

setlocal enabledelayedexpansion

set LAYER_NAME=visitor-management-dependencies
set AWS_REGION=ap-south-1
set BUILD_DIR=build

echo === Deploying Lambda Layer ===
echo.

REM Check if layer zip exists
if not exist "%BUILD_DIR%\%LAYER_NAME%.zip" (
    echo ERROR: Layer zip file not found. Run build-layer.bat first.
    exit /b 1
)

REM Check if AWS CLI is installed
where aws >nul 2>&1
if errorlevel 1 (
    echo ERROR: AWS CLI is not installed
    exit /b 1
)

echo Configuration:
echo   Layer Name: %LAYER_NAME%
echo   Region: %AWS_REGION%
echo   Layer File: %BUILD_DIR%\%LAYER_NAME%.zip
echo.

REM Publish layer
echo Publishing layer to AWS Lambda...
for /f "tokens=*" %%i in ('aws lambda publish-layer-version --layer-name %LAYER_NAME% --description "Dependencies for Visitor Management API" --zip-file fileb://%BUILD_DIR%/%LAYER_NAME%.zip --compatible-runtimes python3.11 --region %AWS_REGION% --query LayerVersionArn --output text') do set LAYER_ARN=%%i

if "!LAYER_ARN!"=="" (
    echo ERROR: Failed to publish layer
    exit /b 1
)

echo.
echo === Layer Deployment Complete ===
echo Layer ARN: !LAYER_ARN!
echo.
echo To use this layer, set it:
echo set LAYER_ARN=!LAYER_ARN!

endlocal
