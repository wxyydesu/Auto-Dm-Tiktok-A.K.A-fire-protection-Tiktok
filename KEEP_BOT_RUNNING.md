# 🔄 KEEP BOT RUNNING - AUTO RESTART GUIDE

## Masalah

Script crash di Termux saat berjalan di tmux, dan tidak auto-restart.

## Solusi

Gunakan wrapper script `run-bot-safe.sh` yang:
- ✅ Auto-restart jika crash
- ✅ Log semua output
- ✅ Track crash statistics
- ✅ Detect crash loops (terlalu banyak crash)
- ✅ Friendly error messages

---

## 🚀 QUICK START

### 1. Setup permissions

```bash
cd /path/to/GMAIL_METHOD
chmod +x run-bot-safe.sh
```

### 2. Jalankan dengan tmux

**Option A: Buat session baru**

```bash
tmux new-session -s tiktok-bot -d "cd /path/to/GMAIL_METHOD && bash run-bot-safe.sh"
```

**Option B: Dari dalam Termux/proot**

```bash
cd /path/to/GMAIL_METHOD
bash run-bot-safe.sh
```

**Option C: Di background dengan nohup**

```bash
cd /path/to/GMAIL_METHOD
nohup bash run-bot-safe.sh > bot_startup.log 2>&1 &
```

### 3. Monitor bot

**View main log (real-time):**
```bash
tail -f bot.log
```

**View error log:**
```bash
tail -f bot_error.log
```

**View crash history:**
```bash
cat bot_crashes.log
```

**View all logs:**
```bash
ls -lh bot*.log
```

---

## 📊 LOG FILES

| File | Purpose |
|------|---------|
| `bot.log` | All output (info + errors + crashes) |
| `bot_error.log` | Only error messages |
| `bot_crashes.log` | Crash history with timestamps |

---

## 🎮 TMUX COMMANDS

```bash
# List sessions
tmux list-sessions

# Attach to session
tmux attach-session -s tiktok-bot

# Detach from session (keep running)
Ctrl+B → D

# Kill session
tmux kill-session -s tiktok-bot

# View pane output
tmux capture-pane -t tiktok-bot -p

# Send command to session
tmux send-keys -t tiktok-bot "command here" Enter
```

---

## 🔧 KONFIGURASI

Edit `run-bot-safe.sh` line ini untuk customize:

```bash
RESTART_DELAY=5              # Delay sebelum restart (detik)
MAX_RESTARTS=999             # Max restart attempts
CRASH_THRESHOLD=5            # Crash limit dalam time window
CRASH_TIME_WINDOW=60         # Time window (detik)
```

**Contoh: Hanya 3 crash dalam 60 detik sebelum stop**

```bash
CRASH_THRESHOLD=3
CRASH_TIME_WINDOW=60
```

---

## 📈 MONITORING SCRIPT

Buat file `monitor-bot.sh`:

```bash
#!/bin/bash

while true; do
    clear
    echo "════════════════════════════════════════════"
    echo "  TIKTOK BOT MONITOR"
    echo "════════════════════════════════════════════"
    echo "Time: $(date)"
    echo ""
    
    echo "📊 Status:"
    if pgrep -f "Tiktok_with_cookies_V2.py" > /dev/null; then
        echo "✅ Bot RUNNING"
    else
        echo "❌ Bot STOPPED"
    fi
    
    echo ""
    echo "📝 Recent Logs (last 10 lines):"
    tail -10 bot.log | sed 's/^/  /'
    
    echo ""
    echo "💥 Crash Count:"
    wc -l bot_crashes.log | awk '{print "  Total: " $1 " crashes"}'
    
    echo ""
    echo "Refresh every 10 seconds... (Press Ctrl+C to exit)"
    sleep 10
done
```

Usage:
```bash
chmod +x monitor-bot.sh
./monitor-bot.sh
```

---

## 🐛 DEBUGGING

### Bot keeps crashing?

1. **Check error log:**
```bash
tail -50 bot_error.log
```

2. **Check last crash:**
```bash
tail -5 bot_crashes.log
```

3. **Run script manually untuk debug:**
```bash
python3 -u Tiktok_with_cookies_V2.py
```

4. **Check Chromium:**
```bash
chromium-browser --version
which chromedriver
```

5. **Check memory:**
```bash
free -h
```

### Too many crashes?

Edit `run-bot-safe.sh`:

```bash
# Increase restart delay
RESTART_DELAY=15  # Dari 5 ke 15 detik

# Increase crash threshold
CRASH_THRESHOLD=10  # Dari 5 ke 10
```

---

## ✅ BEST PRACTICE SETUP

### Full Termux Setup:

```bash
# 1. Login proot
proot-distro login ubuntu

# 2. Navigate
cd /path/to/GMAIL_METHOD

# 3. Make script executable
chmod +x run-bot-safe.sh

# 4. Run in tmux
tmux new-session -s tiktok-bot -d "bash run-bot-safe.sh"

# 5. Attach & verify
tmux attach-session -s tiktok-bot
```

### Monitor dalam session terpisah:

```bash
# Terminal 1: Bot running
tmux attach-session -s tiktok-bot

# Terminal 2: Monitor logs
tail -f bot.log
```

---

## 📱 AUTO-START (Optional)

Untuk auto-start saat Termux dibuka, edit `~/.bashrc`:

```bash
nano ~/.bashrc
```

Tambahkan di akhir:

```bash
# Auto-start TikTok Bot jika belum jalan
if ! pgrep -f "Tiktok_with_cookies_V2.py" > /dev/null; then
    echo "Starting TikTok Bot..."
    cd ~/Auto-Dm-Tiktok/GMAIL_METHOD
    nohup bash run-bot-safe.sh > bot_startup.log 2>&1 &
fi
```

---

## 🎯 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Script tidak auto-restart | Check permissions: `chmod +x run-bot-safe.sh` |
| tmux session closed | Use `tmux list-sessions` to check |
| Log file terlalu besar | `truncate -s 0 bot.log` untuk clear |
| Bot crash terus | Increase `RESTART_DELAY` dan check `bot_error.log` |
| Memory issue | Kill old processes: `killall python3` |

---

## 💡 TIPS

1. **Keep bot running 24/7:**
   - Gunakan tmux di terminal yang tidak di-close
   - Atau gunakan `nohup` untuk background process

2. **Monitor remotely:**
   - Setup SSH jika di remote server
   - Bisa akses logs dari mana saja

3. **Set timezone:**
   ```bash
   export TZ='Asia/Jakarta'
   ```

4. **Rotate logs (daily):**
   ```bash
   # Cron job untuk backup logs harian
   0 0 * * * cd /path/to/GMAIL_METHOD && mv bot.log bot_$(date +\%Y\%m\%d).log
   ```

---

**Sekarang bot akan terus jalan dan auto-restart jika crash!** 🚀
