@echo off
REM Simple script to create a ZIP file of the backend
REM Excludes unnecessary files and folders

setlocal enabledelayedexpansion

set ZIP_NAME=visitor-management-backend.zip
set TEMP_DIR=temp_backend

echo Creating backend ZIP file...

REM Clean previous builds
if exist %ZIP_NAME% del /q %ZIP_NAME%
if exist %TEMP_DIR% rmdir /s /q %TEMP_DIR%

REM Create temporary directory
mkdir %TEMP_DIR%

REM Copy files
echo Copying files...

REM Copy app directory
xcopy /E /I /Y app %TEMP_DIR%\app

REM Copy lambda handler
copy /Y lambda_handler.py %TEMP_DIR%\lambda_handler.py

REM Copy requirements
copy /Y requirements.txt %TEMP_DIR%\requirements.txt

REM Copy configuration files
copy /Y *.yml %TEMP_DIR%\ 2>nul
copy /Y *.yaml %TEMP_DIR%\ 2>nul
copy /Y *.toml %TEMP_DIR%\ 2>nul
copy /Y *.json %TEMP_DIR%\ 2>nul

REM Copy SQL files
copy /Y database_schema.sql %TEMP_DIR%\ 2>nul
copy /Y create_*.sql %TEMP_DIR%\ 2>nul
copy /Y vis_admin_complete.sql %TEMP_DIR%\ 2>nul

REM Remove excluded files and directories
echo Cleaning up excluded files...

REM Remove Python cache (using PowerShell for better reliability)
powershell -Command "Get-ChildItem -Path '%TEMP_DIR%' -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
powershell -Command "Get-ChildItem -Path '%TEMP_DIR%' -Recurse -Filter '*.pyc' | Remove-Item -Force"
powershell -Command "Get-ChildItem -Path '%TEMP_DIR%' -Recurse -Filter '*.pyo' | Remove-Item -Force"
powershell -Command "Get-ChildItem -Path '%TEMP_DIR%' -Recurse -Filter '*.pyd' | Remove-Item -Force"

REM Remove other excluded items
if exist %TEMP_DIR%\.venv rmdir /s /q %TEMP_DIR%\.venv
if exist %TEMP_DIR%\.git rmdir /s /q %TEMP_DIR%\.git
if exist %TEMP_DIR%\.env del /q %TEMP_DIR%\.env
if exist %TEMP_DIR%\node_modules rmdir /s /q %TEMP_DIR%\node_modules
if exist %TEMP_DIR%\tests rmdir /s /q %TEMP_DIR%\tests
if exist %TEMP_DIR%\frontend rmdir /s /q %TEMP_DIR%\frontend
del /q %TEMP_DIR%\*.log 2>nul
del /q %TEMP_DIR%\.DS_Store 2>nul
del /q %TEMP_DIR%\package-lock.json 2>nul

REM Create ZIP file
echo Creating ZIP file...
cd %TEMP_DIR%
powershell -Command "Compress-Archive -Path * -DestinationPath ..\%ZIP_NAME% -Force"
cd ..

REM Clean up temporary directory and exclude list
rmdir /s /q %TEMP_DIR%
del /q exclude_list.txt 2>nul

echo.
echo ZIP file created: %ZIP_NAME%
echo.
echo Files included:
echo   - app/ (application code)
echo   - lambda_handler.py
echo   - requirements.txt
echo   - Configuration files
echo   - SQL schema files
echo.
echo Files excluded:
echo   - .venv/, __pycache__/, .git/
echo   - .env (secrets)
echo   - node_modules/, tests/, frontend/
echo   - *.log, .DS_Store, package-lock.json

endlocal
