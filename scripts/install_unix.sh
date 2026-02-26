#!/bin/bash
# Linux/Mac installation helper for epub2mp3

echo "========================================"
echo "epub2mp3 Installation Helper (Unix)"
echo "========================================"
echo

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MISSING_DEPS=0

# Check Python
echo "[1/5] Checking Python..."
if command -v python3 &> /dev/null; then
    python3 --version
    echo -e "${GREEN}  OK${NC}"
else
    echo -e "${RED}ERROR: Python 3 not found!${NC}"
    echo "Please install Python 3.11+ from your package manager"
    exit 1
fi
echo

# Check Calibre
echo "[2/5] Checking Calibre..."
if command -v ebook-convert &> /dev/null; then
    ebook-convert --version | head -n 1
    echo -e "${GREEN}  OK${NC}"
else
    echo -e "${YELLOW}WARNING: Calibre not found!${NC}"
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install calibre"
    echo "  macOS: brew install calibre"
    MISSING_DEPS=1
fi
echo

# Check FFmpeg
echo "[3/5] Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg -version | head -n 1
    echo -e "${GREEN}  OK${NC}"
else
    echo -e "${YELLOW}WARNING: FFmpeg not found!${NC}"
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    MISSING_DEPS=1
fi
echo

if [ $MISSING_DEPS -eq 1 ]; then
    echo
    echo -e "${RED}IMPORTANT: Please install missing dependencies before continuing.${NC}"
    echo "After installation, run this script again."
    exit 1
fi

# Create virtual environment
echo "[4/5] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}  Virtual environment created${NC}"
else
    echo -e "${YELLOW}  Virtual environment already exists${NC}"
fi
echo

# Activate and install
echo "[5/5] Installing epub2mp3..."
source venv/bin/activate
python -m pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
pip install -e .

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Installation failed!${NC}"
    exit 1
fi

echo
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo
echo "To use epub2mp3:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo
echo "  2. Run the tool:"
echo "     epub2mp3 convert yourbook.epub"
echo
echo "  3. For help:"
echo "     epub2mp3 --help"
echo
echo "Optional: Install Ollama for text cleanup"
echo "  Download from https://ollama.ai"
echo
