@echo off
REM Deploy Lambda Function Package Script for Windows
REM This script uploads the deployment package and updates the Lambda function

setlocal enabledelayedexpansion

if "%LAMBDA_FUNCTION_NAME%"=="" set LAMBDA_FUNCTION_NAME=visitor-management-api
if "%AWS_REGION%"=="" set AWS_REGION=ap-south-1
set PACKAGE_NAME=visitor-management-api
set BUILD_DIR=build

echo === Deploying Lambda Function ===
echo.

REM Check if package zip exists
if not exist "%BUILD_DIR%\%PACKAGE_NAME%.zip" (
    echo ERROR: Package zip file not found. Run build-package.bat first.
    exit /b 1
)

REM Check if AWS CLI is installed
where aws >nul 2>&1
if errorlevel 1 (
    echo ERROR: AWS CLI is not installed
    exit /b 1
)

echo Configuration:
echo   Function Name: %LAMBDA_FUNCTION_NAME%
echo   Region: %AWS_REGION%
echo   Package File: %BUILD_DIR%\%PACKAGE_NAME%.zip
if not "%LAYER_ARN%"=="" (
    echo   Layer ARN: %LAYER_ARN%
)
echo.

REM Check if function exists
aws lambda get-function --function-name %LAMBDA_FUNCTION_NAME% --region %AWS_REGION% >nul 2>&1
if errorlevel 1 (
    echo Function does not exist. Creating new function...
    
    if "%LAMBDA_ROLE_ARN%"=="" (
        echo ERROR: LAMBDA_ROLE_ARN environment variable not set
        echo Create an IAM role for Lambda with basic execution permissions
        exit /b 1
    )
    
    if not "%LAYER_ARN%"=="" (
        aws lambda create-function --function-name %LAMBDA_FUNCTION_NAME% --runtime python3.11 --role %LAMBDA_ROLE_ARN% --handler lambda_handler.lambda_handler --zip-file fileb://%BUILD_DIR%/%PACKAGE_NAME%.zip --timeout 30 --memory-size 512 --layers %LAYER_ARN% --region %AWS_REGION%
    ) else (
        aws lambda create-function --function-name %LAMBDA_FUNCTION_NAME% --runtime python3.11 --role %LAMBDA_ROLE_ARN% --handler lambda_handler.lambda_handler --zip-file fileb://%BUILD_DIR%/%PACKAGE_NAME%.zip --timeout 30 --memory-size 512 --region %AWS_REGION%
    )
    
    if errorlevel 1 (
        echo ERROR: Failed to create function
        exit /b 1
    )
    
    echo Function created successfully
) else (
    echo Updating function code...
    aws lambda update-function-code --function-name %LAMBDA_FUNCTION_NAME% --zip-file fileb://%BUILD_DIR%/%PACKAGE_NAME%.zip --region %AWS_REGION%
    
    if errorlevel 1 (
        echo ERROR: Failed to update function
        exit /b 1
    )
    
    echo Function code updated
    
    if not "%LAYER_ARN%"=="" (
        echo Updating function layers...
        aws lambda update-function-configuration --function-name %LAMBDA_FUNCTION_NAME% --layers %LAYER_ARN% --region %AWS_REGION%
        echo Layers updated
    )
)

echo.
echo === Deployment Complete ===
echo Function: %LAMBDA_FUNCTION_NAME%
echo Region: %AWS_REGION%

endlocal
