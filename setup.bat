@echo off
:: VoxCPM2 OpenAI Speech setup script (Windows)
echo [VoxCPM2] Checking Python version...
python --version 2>nul || (
    echo [VoxCPM2] Error: Python not found. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [VoxCPM2] Python version: %PYVER%

echo [VoxCPM2] Installing dependencies...
pip install httpx -q
echo [VoxCPM2] Installation complete!
echo.
echo Usage:
echo   python voxcpm2_speech.py "Hello, this is VoxCPM2."
echo   python voxcpm2_speech.py "Hello" --ref-audio ref.wav
echo   python voxcpm2_speech.py "Hello" --api-base http://your-server:8000
