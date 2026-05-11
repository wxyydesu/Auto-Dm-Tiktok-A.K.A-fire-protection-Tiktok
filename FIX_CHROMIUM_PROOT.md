# 🔧 FIX CHROMIUM DI PROOT UBUNTU (Termux)

Error yang terjadi:
```
self.version_main = release.version[0]
AttributeError: 'NoneType' object is not subscriptable
```

Ini berarti Chromium tidak terinstall atau tidak terdeteksi dengan baik.

---

## ✅ SOLUSI 1: Install Chromium (Recommended)

### Step 1: Login ke proot Ubuntu

```bash
proot-distro login ubuntu
```

### Step 2: Update package list

```bash
apt update
apt upgrade -y
```

### Step 3: Install Chromium Browser

```bash
apt install -y chromium-browser
```

Atau jika yang di atas tidak work:

```bash
apt install -y chromium
```

### Step 4: Verify instalasi

```bash
which chromium
which chromium-browser

# Atau cek versi
chromium --version
chromium-browser --version
```

**Output yang diharapkan:**
```
/usr/bin/chromium
/usr/bin/chromium-browser
Chromium 125.0.6422.60
```

---

## ⚡ SOLUSI 2: Install dari Snap (Alternative)

Jika apt tidak work:

```bash
apt install snapd

snap install chromium
```

Verifikasi:
```bash
snap list chromium
which chromium
```

---

## 🔍 SOLUSI 3: Manual Binary Download

Jika semua cara di atas tidak work:

```bash
# Download Chromium binary
cd /opt
mkdir -p chromium
cd chromium

# Download dari internet (butuh internet di proot)
wget https://commondatastorage.googleapis.com/chromium-browser-snapshots/Linux_x64/LAST_CHANGE
# atau gunakan curl jika wget tidak ada

# Extract dan setup
chmod +x chrome
ln -s /opt/chromium/chrome /usr/bin/chromium-custom
```

---

## 🛠️ SOLUSI 4: Fix Script Jika Path Berbeda

Script sudah punya fallback untuk multiple paths:

```python
chromium_paths = [
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
    "/opt/chromium/chrome",
]
```

Jika path Chromium di lokasi lain, tambahkan di list:

Edit `Tiktok_with_cookies_V2.py` dan cari section:

```python
# Coba path alternatif
chromium_paths = [
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
    "/opt/chromium/chrome",
]
```

Tambahkan path yang sesuai dengan sistem Anda.

---

## 📝 Troubleshooting

### Error: "Chromium not found in standard paths"

**Solusi:**
```bash
# Cari lokasi Chromium
find /usr -name "chromium*" 2>/dev/null
find / -name "chromium" -type f 2>/dev/null

# Atau gunakan
whereis chromium
```

Setelah menemukan lokasi, update path di script.

### Error: "Cannot connect to display :99"

**Solusi:**
Script sudah set `DISPLAY=:99` dan menggunakan `--headless=new`, jadi ini seharusnya tidak jadi masalah.

Jika masih error, coba:

```bash
# Disable display altogether
unset DISPLAY
python3 Tiktok_with_cookies_V2.py
```

### Error: "Out of memory" saat membuka Chromium

**Solusi:**
Script sudah pakai flags untuk resource yang limited:
- `--single-process`
- `--no-zygote`
- `--disable-dev-shm-usage`

Jika masih OOM:

1. **Upgrade swap di proot:**
```bash
# Check current swap
free -h

# Increase swap (jika ada)
dd if=/dev/zero of=/swapfile bs=1G count=2
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

2. **Kill other processes:**
```bash
# Check memory usage
ps aux --sort=-%mem | head -20

# Kill unnecessary processes
killall [process_name]
```

### Error: "Failed to start GPU process"

**Solusi:**
Script sudah disable GPU dengan flag:
- `--disable-gpu`
- `--disable-software-rasterizer`

Jika masih error, ensure flags sudah di-add dengan benar.

---

## ✨ Verifikasi Setelah Setup

```bash
# 1. Login ke proot
proot-distro login ubuntu

# 2. Check Chromium
chromium --version

# 3. Test dry-run jika perlu
chromium --headless --no-sandbox --screenshot /tmp/test.png https://www.google.com

# 4. Jalankan script
cd /path/to/Auto-Dm-Tiktok
python3 Tiktok_with_cookies_V2.py
```

---

## 📊 Quick Reference

| Issue | Solution |
|-------|----------|
| Chromium not found | `apt install chromium-browser` |
| Version detection fail | Auto fallback ke path alternatif |
| Display error | `--headless=new` mode (tidak butuh display) |
| Out of memory | Reduce chrome args atau upgrade swap |
| Permission denied | `chmod +x /usr/bin/chromium` |

---

## 🚀 Best Practice Setup

```bash
# 1. Cleanup old resources
rm -rf ~/.cache/chromium
rm -rf /root/.chromium-cache

# 2. Ensure writable permission
mkdir -p /root/tiktok-profile
chmod 777 /root/tiktok-profile

# 3. Run script
python3 Tiktok_with_cookies_V2.py
```

---

**After setup, script akan automatically detect dan use Chromium!** ✅

Jika masih ada issue, cek output error message - script sekarang provide helpful hints. 💡
