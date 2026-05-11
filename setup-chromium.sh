#!/bin/bash

# Auto setup Chromium di proot Ubuntu untuk TikTok Auto DM
# Run ini di dalam proot Ubuntu

echo "=================================================="
echo "  AUTO SETUP CHROMIUM - TIKTOK AUTO DM"
echo "=================================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Script harus dijalankan sebagai root!"
   echo "   Coba: sudo bash setup-chromium.sh"
   exit 1
fi

echo "[1/5] Update package list..."
apt update -qq
if [ $? -ne 0 ]; then
    echo "❌ Gagal update package list!"
    exit 1
fi
echo "✅ Package list updated"

echo ""
echo "[2/5] Upgrade packages..."
apt upgrade -y -qq
if [ $? -ne 0 ]; then
    echo "⚠️  Upgrade gagal (non-critical, melanjutkan...)"
fi
echo "✅ Packages upgraded"

echo ""
echo "[3/5] Install dependencies..."
apt install -y -qq \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    libnss3 \
    ca-certificates \
    wget \
    curl

if [ $? -ne 0 ]; then
    echo "❌ Gagal install dependencies!"
    exit 1
fi
echo "✅ Dependencies installed"

echo ""
echo "[4/5] Install Chromium browser..."
apt install -y chromium-browser
INSTALL_STATUS=$?

if [ $INSTALL_STATUS -eq 0 ]; then
    echo "✅ Chromium browser installed successfully!"
else
    echo "⚠️  chromium-browser installation failed, trying chromium..."
    apt install -y chromium
    if [ $? -ne 0 ]; then
        echo "❌ Both chromium-browser dan chromium gagal di-install!"
        echo "   Coba install manual: apt install chromium-browser"
        exit 1
    fi
fi

echo ""
echo "[5/5] Verifikasi instalasi..."
CHROMIUM_PATH=$(which chromium)
CHROMIUM_BROWSER_PATH=$(which chromium-browser)

if [ -z "$CHROMIUM_PATH" ] && [ -z "$CHROMIUM_BROWSER_PATH" ]; then
    echo "❌ Chromium tidak ditemukan di system PATH!"
    echo "   Coba cek dengan:"
    echo "     find /usr -name chromium* -type f"
    exit 1
fi

if [ -n "$CHROMIUM_PATH" ]; then
    echo "✅ chromium found at: $CHROMIUM_PATH"
    CHROMIUM_VERSION=$($CHROMIUM_PATH --version)
    echo "   Version: $CHROMIUM_VERSION"
fi

if [ -n "$CHROMIUM_BROWSER_PATH" ]; then
    echo "✅ chromium-browser found at: $CHROMIUM_BROWSER_PATH"
    CHROMIUM_BROWSER_VERSION=$($CHROMIUM_BROWSER_PATH --version)
    echo "   Version: $CHROMIUM_BROWSER_VERSION"
fi

echo ""
echo "=================================================="
echo "  ✅ SETUP SELESAI!"
echo "=================================================="
echo ""
echo "Chromium sudah siap digunakan."
echo ""
echo "Langkah selanjutnya:"
echo "1. Exit dari proot: exit"
echo "2. Jalankan script: python3 Tiktok_with_cookies_V2.py"
echo ""
echo "Atau untuk test Chromium:"
echo "  chromium --headless --no-sandbox --screenshot /tmp/test.png https://www.google.com"
echo ""
