# 📱 TIKTOK AUTO DM - PANDUAN INSTALASI

## ⚙️ Persyaratan Sistem

### Opsi 1: Windows/Mac/Linux (Desktop)

- Python 3.8 atau lebih tinggi
- Google Chrome atau Chromium
- pip (Python package manager)

### Opsi 2: Termux (Android dengan proot)

- Termux aplikasi (dari F-Droid)
- Paket proot-distro
- Ubuntu distro (atau Linux lainnya)
- Python 3.8+

---

## 🚀 INSTALASI

### STEP 1: Persiapan Lingkungan

#### Untuk Windows/Mac/Linux:

```bash
# Clone atau download folder project
cd Auto DM Tiktok/GMAIL_METHOD

# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

#### Untuk Termux (proot Ubuntu):

```bash
# Buka Termux dan masuk ke proot Ubuntu
proot-distro login ubuntu

# Update paket
apt update && apt upgrade

# Install Python dan dependencies
apt install python3 python3-pip python3-dev

# Navigasi ke project folder
cd /path/to/Auto DM Tiktok/GMAIL_METHOD
```

---

### STEP 2: Instalasi Dependencies

Jalankan command berikut (sama untuk semua sistem):

```bash
pip install requests
pip install selenium
pip install schedule
pip install undetected-chromedriver
```

Atau gunakan requirements.txt (jika tersedia):

```bash
pip install -r requirements.txt
```

**Daftar Package:**

- `requests` - HTTP library
- `selenium` - Browser automation
- `schedule` - Job scheduling
- `undetected-chromedriver` - Undetected Chrome driver (anti-bot bypass)

---

### STEP 3: Persiapan Cookies

Script memerlukan cookies dari akun TikTok Anda.

#### Cara Mendapatkan Cookies:

1. **Install Extension EditThisCookie**

   - Buka Chrome/Chromium
   - Buka [Chrome Web Store - EditThisCookie](https://chrome.google.com/webstore)
   - Cari "EditThisCookie" dan install
2. **Export Cookies dari TikTok**

   - Buka https://www.tiktok.com
   - Login dengan akun TikTok Anda
   - Klik icon **EditThisCookie** di top-right browser
   - Klik tombol **Export** (icon panah keluar)
   - Klik **Copy as JSON**
   - Cookies sudah di-copy ke clipboard
3. **Jalankan Script Pertama Kali**

   ```bash
   python Tiktok_with_cookies_V2.py
   ```
4. **Pilih Opsi 1 (Belum ada cookies)**

   - Script akan meminta Anda paste cookies JSON
   - Paste hasil dari EditThisCookie
   - Ketik `done` jika sudah selesai paste
   - Cookies akan disimpan di `cookies_backup.json`

---

## ▶️ CARA MENGGUNAKAN

### Jalankan Script:

```bash
python Tiktok_with_cookies_V2.py
```

### Menu Utama:

```
==========================================================
  TIKTOK AUTO DM - BY WXYYDESU
==========================================================

> Username target (tanpa @): [KETIK USERNAME]
> Pesan yang akan dikirim: [KETIK PESAN]

PILIH METODE PENGIRIMAN
1. Kirim sekarang
2. Jadwalkan pengiriman
```

---

### Opsi 1: Kirim DM Sekarang

1. Pilih `1`
2. Masukkan username target (tanpa @)
3. Masukkan pesan
4. Konfirmasi dengan `y` atau `n`
5. Script akan membuka browser dan mengirim DM

**Output:**

- Screenshot akan disimpan di folder project
- Log pengiriman di `dm_log.txt`

---

### Opsi 2: Jadwalkan Pengiriman

#### Tipe Daily (Setiap Hari)

1. Pilih `2` → `1`
2. Masukkan jam (0-23)
3. Masukkan menit (0-59)
4. Konfirmasi dengan `y`
5. Script akan berjalan terus dan mengirim DM pada jam yang ditentukan

**Contoh:**

```
Jam: 10
Menit: 30
→ DM akan dikirim setiap hari pukul 10:30
```

#### Tipe Weekly (Setiap Minggu)

1. Pilih `2` → `2`
2. Pilih hari (1-7)
   - 1 = Senin
   - 2 = Selasa
   - ... dst
   - 7 = Minggu
3. Masukkan jam (0-23)
4. Masukkan menit (0-59)
5. Konfirmasi dengan `y`

**Contoh:**

```
Hari: 5 (Jumat)
Jam: 14
Menit: 00
→ DM akan dikirim setiap Jumat pukul 14:00
```

---

## 🐧 SETUP UNTUK TERMUX (Android)

### Instalasi Awal:

```bash
# 1. Buka Termux dan install proot-distro
pkg install proot-distro

# 2. Install Ubuntu
proot-distro install ubuntu

# 3. Login ke Ubuntu
proot-distro login ubuntu

# 4. Update & install dependencies
apt update && apt upgrade
apt install python3 python3-pip python3-dev wget curl

# 5. Clone/copy project ke Termux
# Gunakan scp, git clone, atau copy manual
```

### Instalasi Package Python:

```bash
pip3 install requests selenium schedule undetected-chromedriver
```

### Setup Display Server (Untuk Headless):

Script sudah menyertakan:

```python
os.environ['DISPLAY'] = ':99'
```

Ini memungkinkan Chrome berjalan tanpa GUI di Termux.

### Jalankan Script:

```bash
python3 Tiktok_with_cookies_V2.py
```

---

## 📁 Struktur File

```
GMAIL_METHOD/
├── Tiktok_with_cookies_V2.py     ← Script utama
├── cookies_backup.json           ← File cookies (auto-generated)
├── dm_log.txt                    ← Log pengiriman DM
├── readme-Instalasi.md           ← File ini
└── screenshots/
    ├── 01_profile_page.png
    ├── 02_no_message_button.png
    ├── 03_no_textarea.png
    └── dm_sent_username_*.png
```

---

## 🔧 Troubleshooting

### Error: "File cookies_backup.json tidak ditemukan"

**Solusi:**

- Jalankan script dan pilih opsi 1 untuk membuat cookies
- Paste cookies dari EditThisCookie

### Error: "Textarea tidak ditemukan"

**Kemungkinan Penyebab:**

- HTML TikTok berubah
- Timeout terlalu singkat
- Akun target tidak bisa di-DM

**Solusi:**

- Tunggu beberapa detik sebelum mengirim
- Cek apakah akun target bisa menerima DM
- Lihat screenshot `03_no_textarea.png`

### Error: "Tombol Message tidak ditemukan"

**Penyebab:** Akun target tidak bisa di-DM (privacy setting)

**Solusi:**

- Ubah akun target
- Lihat screenshot `02_no_message_button.png`

### Chrome crashes di Termux

**Solusi:**

```bash
# Gunakan argument tambahan di ChromeOptions:
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Sudah ada di script V2!
```

### Cookies expired/tidak valid

**Solusi:**

- Delete `cookies_backup.json`
- Jalankan script lagi dan update cookies dengan export baru dari EditThisCookie

---

## ⏰ Tips Penggunaan

### 1. Best Practices

```python
# Jangan spam DM (bisa kena ban)
- Tunggu 5-10 detik antar pengiriman
- Gunakan pesan yang natural
- Jangan kirim ke terlalu banyak orang sekaligus
```

### 2. Backup Cookies

```bash
# Jika akun penting, backup cookies secara berkala
cp cookies_backup.json cookies_backup_$(date +%Y%m%d).json
```

### 3. Monitoring Log

```bash
# Lihat log pengiriman
cat dm_log.txt

# Monitor real-time
tail -f dm_log.txt
```

---

## 🆘 Support

Jika mengalami masalah:

1. **Cek log di console** - Catat pesan error
2. **Lihat screenshots** - Folder project akan auto-generated
3. **Periksa dm_log.txt** - Lihat history pengiriman
4. **Update Chrome** - Pastikan Chrome terbaru
5. **Update undetected-chromedriver**:
   ```bash
   pip install --upgrade undetected-chromedriver
   ```

---

## 📝 Catatan Penting

⚠️ **DISCLAIMER:**

- Script ini untuk tujuan edukasi
- Gunakan dengan bijak dan tidak untuk spam
- TikTok bisa ban akun yang spam/abuse
- Gunakan cookies dengan aman dan jangan share
- Backup cookies Anda secara berkala

---

## 🔄 Update Log

### V2 (Current)

- ✅ Menggunakan `undetected-chromedriver`
- ✅ Support Termux dengan proot Ubuntu
- ✅ Display environment variable untuk headless mode
- ✅ Better selector detection
- ✅ Improved error handling
- ✅ Auto-logging & screenshot

---

**Terima kasih telah menggunakan TIKTOK AUTO DM!** 🎉

Selamat mencoba! Jika ada pertanyaan, silakan cek log atau screenshot untuk debugging.
