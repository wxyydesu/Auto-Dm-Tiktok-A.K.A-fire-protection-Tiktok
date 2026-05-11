# 🐧 SETUP TMUX + WAKE CLOCK di TERMUX

Panduan lengkap menjalankan TikTok Auto DM dengan tmux dan wake clock di Termux (proot Ubuntu).

---

## 📋 Prerequisites

- ✅ Termux sudah terinstall
- ✅ proot-distro dengan Ubuntu sudah setup
- ✅ Python 3 + dependencies sudah installed
- ✅ Script `Tiktok_with_cookies_V2.py` sudah ada

---

## 🔧 STEP 1: Install tmux di Termux

```bash
# Login ke proot Ubuntu
proot-distro login ubuntu

# Update package list
apt update

# Install tmux
apt install tmux

# Verify installation
tmux --version
```

---

## 🚀 STEP 2: Setup Tmux Session untuk Script

### Opsi A: Jalankan Manual (Cepat)

```bash
# 1. Buat session tmux baru
tmux new-session -d -s tiktok-dm

# 2. Jalankan script di dalam session
tmux send-keys -t tiktok-dm "cd /path/to/GMAIL_METHOD && python3 Tiktok_with_cookies_V2.py" Enter

# 3. Attach ke session untuk lihat output
tmux attach-session -t tiktok-dm

# Untuk detach (keluar dari session): Ctrl+B kemudian D
```

### Opsi B: Setup Script Startup (Otomatis di Reboot)

Buat file `~/start-tiktok-dm.sh`:

```bash
#!/bin/bash

# Start tmux session
tmux new-session -d -s tiktok-dm

# Set working directory
tmux send-keys -t tiktok-dm "cd /root/path-to-GMAIL_METHOD" Enter

# Wait for directory to be ready
sleep 1

# Run Python script
tmux send-keys -t tiktok-dm "python3 Tiktok_with_cookies_V2.py" Enter

# Log to file
echo "[$(date)] TikTok Auto DM started in tmux session" >> ~/tiktok-dm-startup.log
```

Simpan dan buat executable:

```bash
chmod +x ~/start-tiktok-dm.sh
```

---

## ⏰ STEP 3: Setup Wake Clock (Device Tetap Aktif)

### Opsi A: Gunakan termux-wake-lock

```bash
# Install termux-wake-lock package
pkg install termux-wake-lock

# Di dalam tmux session, jalankan sebelum script:
termux-wake-lock

# Script akan tetap jalan meski device lock
```

### Opsi B: Gunakan wakelocks di proot Ubuntu

```bash
# Login Ubuntu
proot-distro login ubuntu

# Install tools
apt install wakeonlan curl

# Di script, tambahkan di awal:
# Cek power status
cat /sys/power/state

# Atau gunakan systemd untuk prevent sleep
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### Opsi C: Gunakan at/cron untuk Scheduled Execution

```bash
# Install cron
apt install cron

# Mulai cron daemon
service cron start

# Edit crontab
crontab -e

# Tambahkan (contoh: setiap jam 10:30)
30 10 * * * /path/to/GMAIL_METHOD/run-dm.sh >> /tmp/tiktok-dm.log 2>&1
```

---

## 🎯 STEP 4: Kombinasi Tmux + Wake Clock (Rekomendasi)

Buat script `run-tiktok-dm.sh`:

```bash
#!/bin/bash

# Enable wake lock
termux-wake-lock

# Create tmux session
SESSION="tiktok-dm"

# Kill old session if exists
tmux kill-session -t $SESSION 2>/dev/null

# Create new session
tmux new-session -d -s $SESSION -c "/root/GMAIL_METHOD"

# Run script
tmux send-keys -t $SESSION "python3 Tiktok_with_cookies_V2.py" Enter

# Log activity
echo "[$(date)] Session $SESSION started with wake lock enabled" >> ~/tiktok-dm-log.txt

# Keep script running
while true; do
    if ! tmux has-session -t $SESSION 2>/dev/null; then
        echo "[$(date)] Session crashed, restarting..." >> ~/tiktok-dm-log.txt
        tmux new-session -d -s $SESSION -c "/root/GMAIL_METHOD"
        tmux send-keys -t $SESSION "python3 Tiktok_with_cookies_V2.py" Enter
    fi
    sleep 300  # Check every 5 minutes
done
```

Jalankan:

```bash
chmod +x run-tiktok-dm.sh
./run-tiktok-dm.sh
```

---

## 📱 STEP 5: Atur Otomatis Startup (Saat Termux Dibuka)

Edit `~/.profile` atau `~/.bashrc`:

```bash
nano ~/.profile
```

Tambahkan di akhir:

```bash
# Auto-start TikTok Auto DM
if [ -z "$TMUX" ]; then
    echo "Starting TikTok Auto DM session..."
    tmux new-session -d -s tiktok-dm -c "/root/GMAIL_METHOD"
    tmux send-keys -t tiktok-dm "python3 Tiktok_with_cookies_V2.py" Enter
    echo "Session started. Use 'tmux attach-session -t tiktok-dm' to view"
fi
```

---

## 🎮 Tmux Commands Reference

```bash
# Buat session baru
tmux new-session -d -s session-name

# List semua session
tmux list-sessions

# Attach ke session
tmux attach-session -t session-name

# Detach (keluar dari session)
Ctrl+B → D

# Kill session
tmux kill-session -t session-name

# Send command ke session
tmux send-keys -t session-name "command" Enter

# Create window di session
tmux new-window -t session-name -n window-name

# List windows
tmux list-windows -t session-name

# Navigate windows
Ctrl+B → n (next)
Ctrl+B → p (previous)
Ctrl+B → 0-9 (jump ke window)
```

---

## 📊 Setup Monitoring

### Script untuk Monitor Session:

```bash
#!/bin/bash
# monitor-tiktok-dm.sh

SESSION="tiktok-dm"

while true; do
    clear
    echo "=== TikTok Auto DM Monitor ==="
    echo "Current Time: $(date)"
    echo ""
    
    # Check if session exists
    if tmux has-session -t $SESSION 2>/dev/null; then
        echo "✅ Session Status: RUNNING"
        echo ""
        echo "--- Session Output ---"
        tmux capture-pane -t $SESSION -p
    else
        echo "❌ Session Status: STOPPED"
    fi
    
    echo ""
    echo "Refresh every 10 seconds..."
    sleep 10
done
```

Jalankan di session terpisah:

```bash
chmod +x monitor-tiktok-dm.sh
./monitor-tiktok-dm.sh
```

---

## 🔄 Setup Systemd Service (Advanced)

Buat `/etc/systemd/system/tiktok-dm.service`:

```ini
[Unit]
Description=TikTok Auto DM Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/GMAIL_METHOD
ExecStart=/usr/bin/python3 /root/GMAIL_METHOD/Tiktok_with_cookies_V2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activate:

```bash
systemctl daemon-reload
systemctl enable tiktok-dm.service
systemctl start tiktok-dm.service

# Check status
systemctl status tiktok-dm.service

# View logs
journalctl -u tiktok-dm.service -f
```

---

## ⚡ Quick Start (Recommended Flow)

### Session 1: Terminal Tmux

```bash
# Login Termux → Ubuntu
proot-distro login ubuntu

# Install tmux
apt install tmux termux-wake-lock

# Navigate to project
cd /root/GMAIL_METHOD

# Create tmux session
tmux new-session -s tiktok-dm

# Di dalam session, jalankan:
termux-wake-lock
python3 Tiktok_with_cookies_V2.py

# Detach: Ctrl+B → D
```

### Session 2: Monitor (Optional)

```bash
# Di terminal lain, attach ke session
tmux attach-session -t tiktok-dm

# Lihat output real-time
```

### Session 3: Backup/Logs

```bash
# Monitor log files
tail -f dm_log.txt
tail -f tiktok-dm-log.txt
```

---

## 🛡️ Tips & Tricks

### 1. Prevent Timeout

Tambahkan di script sebelum `while True`:

```python
# Keep session alive
import signal
signal.alarm(0)  # Cancel any alarms
```

### 2. Auto-Reconnect pada Network Loss

```bash
# Di wrapper script
while true; do
    tmux send-keys -t tiktok-dm "python3 Tiktok_with_cookies_V2.py" Enter
    sleep 300
done
```

### 3. Logging & Monitoring

```bash
# Redirect output
tmux send-keys -t tiktok-dm "python3 Tiktok_with_cookies_V2.py 2>&1 | tee -a tiktok-dm-full.log" Enter
```

### 4. Graceful Shutdown

```bash
# Script graceful stop
tmux send-keys -t tiktok-dm "C-c"  # Send Ctrl+C
sleep 2
tmux kill-session -t tiktok-dm
```

---

## 📝 Example: Complete Setup

```bash
# 1. Login Termux
termux-wake-lock

# 2. Login Ubuntu di proot
proot-distro login ubuntu

# 3. Install dependencies
apt update && apt install python3 python3-pip tmux

# 4. Install Python packages
pip3 install requests selenium schedule undetected-chromedriver

# 5. Navigate to project
cd /root/GMAIL_METHOD

# 6. Create tmux session
tmux new-session -d -s tiktok-dm

# 7. Start script in background
tmux send-keys -t tiktok-dm "python3 Tiktok_with_cookies_V2.py" Enter

# 8. Verify running
tmux list-sessions

# 9. Attach to view
tmux attach-session -t tiktok-dm

# 10. Detach (keep running)
# Ctrl+B → D
```

---

## 🔍 Troubleshooting

### tmux tidak ketemu

```bash
# Install tmux
apt install tmux -y

# Verify
tmux --version
```

### Script berhenti saat device sleep

```bash
# Pastikan wake lock enabled
termux-wake-lock

# Atau disable sleep:
sudo systemctl mask sleep.target
```

### Permission denied

```bash
# Give execute permission
chmod +x ~/run-tiktok-dm.sh

# Run with sudo jika diperlukan
sudo ./run-tiktok-dm.sh
```

### Session crash

```bash
# Check session status
tmux list-sessions

# Kill old session
tmux kill-session -t tiktok-dm

# Restart
tmux new-session -d -s tiktok-dm
tmux send-keys -t tiktok-dm "python3 Tiktok_with_cookies_V2.py" Enter
```

---

**Happy Automating!** 🚀

Gunakan setup ini untuk menjalankan script 24/7 di Termux tanpa khawatir device tidur atau session crash.
