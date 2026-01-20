@echo off
REM Complete Deployment Script for Windows
REM Deploys ZIP to Lambda and updates API Gateway

setlocal enabledelayedexpansion

set FUNCTION_NAME=visitor-management-api
set REGION=ap-south-1
set STAGE=prod
set ZIP_FILE=visitor-management-backend.zip

echo === Complete Lambda Deployment ===
echo.

REM Check if ZIP file exists
if not exist "%ZIP_FILE%" (
    echo ERROR: ZIP file not found: %ZIP_FILE%
    echo Please run create-zip.bat first
    exit /b 1
)

REM Step 1: Update Lambda function code
echo Step 1: Uploading ZIP to Lambda...
aws lambda update-function-code ^
  --function-name %FUNCTION_NAME% ^
  --zip-file fileb://%ZIP_FILE% ^
  --region %REGION%

if errorlevel 1 (
    echo ERROR: Failed to update function code
    exit /b 1
)

REM Step 2: Wait for update
echo Step 2: Waiting for function update...
timeout /t 5 /nobreak >nul
aws lambda wait function-updated --function-name %FUNCTION_NAME% --region %REGION%

echo.
echo === Deployment Complete ===
echo Function: %FUNCTION_NAME%
echo Region: %REGION%
echo.
echo Next steps:
echo 1. Configure environment variables in Lambda Console
echo 2. Set up API Gateway (see DEPLOYMENT_STEPS.md)
echo 3. Test the function

endlocal
