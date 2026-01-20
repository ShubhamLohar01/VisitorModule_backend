@echo off
REM Complete Deployment Script for Windows
REM Builds layer, builds package, and deploys everything

setlocal enabledelayedexpansion

echo === Complete Lambda Deployment ===
echo.

REM Step 1: Build Layer
echo Step 1: Building Lambda Layer...
call build-layer.bat
if errorlevel 1 (
    echo ERROR: Failed to build layer
    exit /b 1
)

REM Step 2: Deploy Layer
echo.
echo Step 2: Deploying Lambda Layer...
call deploy-layer.bat > layer_output.txt 2>&1
for /f "tokens=*" %%i in ('findstr "Layer ARN:" layer_output.txt') do (
    set LINE=%%i
    for /f "tokens=2 delims=:" %%j in ("!LINE!") do set LAYER_ARN=%%j
    set LAYER_ARN=!LAYER_ARN: =!
)

if "!LAYER_ARN!"=="" (
    echo ERROR: Failed to get Layer ARN
    type layer_output.txt
    exit /b 1
)

set LAYER_ARN=!LAYER_ARN!
echo Using Layer ARN: !LAYER_ARN!
echo.

REM Step 3: Build Package
echo Step 3: Building Deployment Package...
call build-package.bat
if errorlevel 1 (
    echo ERROR: Failed to build package
    exit /b 1
)

REM Step 4: Deploy Package
echo.
echo Step 4: Deploying Lambda Function...
set LAYER_ARN=!LAYER_ARN!
call deploy-package.bat
if errorlevel 1 (
    echo ERROR: Failed to deploy package
    exit /b 1
)

del layer_output.txt 2>nul

echo.
echo === All Deployments Complete ===

endlocal
