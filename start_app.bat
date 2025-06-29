@echo off
title AI Character Chatbot - Startup Script

echo ================================================
echo   AI Character Chatbot - Startup Script
echo ================================================
echo.

:: 現在のディレクトリをスクリプトの場所に変更
cd /d "%~dp0"

:: requirements.txtの存在確認
echo [1/4] Requirements file check...
if not exist "requirements.txt" (
    echo Error: requirements.txt not found in current directory.
    echo Current directory: %CD%
    echo Please make sure you are running this from the correct folder.
    pause
    exit /b 1
)

:: 仮想環境の確認
echo [2/4] Virtual environment check...
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        echo Please check if Python is installed correctly.
        pause
        exit /b 1
    )
)

:: 仮想環境の有効化
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

:: 依存関係のインストール
echo [4/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some packages may have failed to install.
    pause
)

:: Stable Diffusion WebUIの起動確認
echo [5/6] Checking Stable Diffusion WebUI...
set "SD_PATH=C:\Users\kohar\Downloads\stable-diffusion-webui-1.10.1"
if exist "%SD_PATH%\webui-user.bat" (
    echo Stable Diffusion WebUI found. Starting in new window...
    start "Stable Diffusion WebUI" cmd /c "cd /d %SD_PATH% && webui-user.bat"
    echo Waiting for Stable Diffusion API...
    :loop
    curl -s http://127.0.0.1:7860/sdapi/v1/options >nul 2>nul
    if errorlevel 1 (
        timeout /t 5 >nul
        goto loop
    )
    echo Stable Diffusion API is up!
) else (
    echo Stable Diffusion WebUI not found.
    echo Expected path: %SD_PATH%
    echo You can start it manually if needed.
)

echo.
echo ================================================
echo   Starting Streamlit App...
echo ================================================
echo.
echo Once the app starts, access it at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the app.
echo.

:: Streamlitアプリの起動
echo [6/6] Launching Streamlit...
streamlit run app.py --server.port 8501 --server.address localhost

:: 終了処理
echo.
echo App has been terminated.
pause
