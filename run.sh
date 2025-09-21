#!/bin/bash

echo "========================================"
echo "  AI ToolBox"
echo "  Starting Application..."
echo "========================================"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from your package manager"
    exit 1
fi

# Sanal ortam oluştur (opsiyonel)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Sanal ortamı etkinleştir
source venv/bin/activate

# Gereksinimleri yükle
echo "Installing requirements..."
pip install -r requirements.txt

# Uygulamayı başlat
echo "Starting AI ToolBox..."
python main.py

echo "Application closed."
