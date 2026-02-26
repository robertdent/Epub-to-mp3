@echo off
REM Windows installation helper for epub2mp3
REM Run this script to check dependencies and install epub2mp3

echo ========================================
echo epub2mp3 Installation Helper (Windows)
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Check Calibre
echo [2/5] Checking Calibre...
ebook-convert --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Calibre not found!
    echo Please install from https://calibre-ebook.com/download_windows
    echo Then add it to your PATH or restart this script
    set MISSING_DEPS=1
) else (
    ebook-convert --version | findstr /C:"ebook-convert"
    echo   OK
)
echo.

REM Check FFmpeg
echo [3/5] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found!
    echo Please install from https://ffmpeg.org/download.html
    echo Then add it to your PATH or restart this script
    set MISSING_DEPS=1
) else (
    ffmpeg -version | findstr /C:"ffmpeg version"
    echo   OK
)
echo.

if defined MISSING_DEPS (
    echo.
    echo IMPORTANT: Please install missing dependencies before continuing.
    echo After installation, restart this script.
    pause
    exit /b 1
)

REM Create virtual environment
echo [4/5] Creating Python virtual environment...
if not exist venv (
    python -m venv venv
    echo   Virtual environment created
) else (
    echo   Virtual environment already exists
)
echo.

REM Activate and install
echo [5/5] Installing epub2mp3...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
pip install -e .

if errorlevel 1 (
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To use epub2mp3:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Run the tool:
echo      epub2mp3 convert yourbook.epub
echo.
echo   3. For help:
echo      epub2mp3 --help
echo.
echo Optional: Install Ollama for text cleanup
echo   Download from https://ollama.ai
echo.

pause
