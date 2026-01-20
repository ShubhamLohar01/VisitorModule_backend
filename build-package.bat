@echo off
REM Build Lambda Deployment Package Script for Windows
REM This script creates a ZIP file with only the application code

setlocal enabledelayedexpansion

set PACKAGE_NAME=visitor-management-api
set BUILD_DIR=build
set PACKAGE_DIR=package

echo === Building Lambda Deployment Package ===
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist %PACKAGE_DIR% rmdir /s /q %PACKAGE_DIR%
mkdir %PACKAGE_DIR%
if not exist %BUILD_DIR% mkdir %BUILD_DIR%

REM Copy application code
echo Copying application code...
xcopy /E /I /Y app %PACKAGE_DIR%\app
copy /Y lambda_handler.py %PACKAGE_DIR%\lambda_handler.py

REM Create zip file
echo Creating deployment package...
cd %PACKAGE_DIR%
powershell -Command "Compress-Archive -Path * -DestinationPath ..\%BUILD_DIR%\%PACKAGE_NAME%.zip -Force"
cd ..

echo.
echo === Package Build Complete ===
echo Package file: %BUILD_DIR%\%PACKAGE_NAME%.zip
echo Next step: Deploy using deploy-package.bat

endlocal
