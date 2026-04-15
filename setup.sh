#!/usr/bin/env bash
# VoxCPM2 OpenAI Speech 一键安装脚本 (Linux/macOS)
set -e

echo "[VoxCPM2] Checking Python version..."
if ! command -v python3 &>/dev/null; then
    echo "[VoxCPM2] Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

PYVER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[VoxCPM2] Python version: $PYVER"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "[VoxCPM2] Python version OK"
else
    echo "[VoxCPM2] Error: Python >= 3.8 required, current $PYVER"
    exit 1
fi

echo "[VoxCPM2] Installing dependencies..."
python3 -m pip install httpx -q
echo "[VoxCPM2] Installation complete!"
echo ""
echo "Usage:"
echo "  python3 voxcpm2_speech.py 'Hello, this is VoxCPM2.'"
echo "  python3 voxcpm2_speech.py 'Hello' --ref-audio ref.wav"
echo "  python3 voxcpm2_speech.py 'Hello' --api-base http://your-server:8000"
