@echo off
title Stable Diffusion WebUI - Startup

echo ================================================
echo   Stable Diffusion WebUI - Startup Script
echo ================================================
echo.

:: Stable Diffusion WebUIのパス設定
set "SD_DIR=C:\Users\kohar\Downloads\stable-diffusion-webui-1.10.1"
set "SD_BATCH=%SD_DIR%\webui-user.bat"

:: パスの存在確認
if not exist "%SD_BATCH%" (
    echo Error: Stable Diffusion WebUI not found.
    echo Expected path: %SD_BATCH%
    echo.
    echo Solutions:
    echo 1. Install Stable Diffusion WebUI
    echo 2. Update the SD_DIR path in this batch file
    echo.
    pause
    exit /b 1
)

:: ディレクトリ移動
cd /d "%SD_DIR%"

echo Starting Stable Diffusion WebUI...
echo Initial startup may take some time.
echo.
echo Once started, access it at:
echo http://localhost:7860
echo.
echo Press Ctrl+C to stop.
echo.

:: WebUI起動
call webui-user.bat

echo.
echo Stable Diffusion WebUI has been terminated.
pause
