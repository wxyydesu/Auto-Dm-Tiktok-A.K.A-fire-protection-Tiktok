#!/bin/bash

# Quick reference commands untuk keep bot running

# ============================================
# 🚀 START BOT
# ============================================

# Dalam Termux proot:
cd /path/to/GMAIL_METHOD
bash run-bot-safe.sh

# Atau dalam tmux:
tmux new-session -s tiktok-bot -d "cd /path/to/GMAIL_METHOD && bash run-bot-safe.sh"

# ============================================
# 📊 MONITOR BOT
# ============================================

# Real-time log
tail -f bot.log

# Last 50 lines
tail -50 bot.log

# Search for errors
grep "❌" bot.log
grep "Error" bot_error.log

# Count crashes
wc -l bot_crashes.log

# ============================================
# 🎮 TMUX COMMANDS
# ============================================

# List all sessions
tmux list-sessions

# Attach to session
tmux attach-session -s tiktok-bot

# Detach (keep running)
# Press: Ctrl+B → D

# Kill session
tmux kill-session -s tiktok-bot

# View session output
tmux capture-pane -t tiktok-bot -p

# ============================================
# 🛑 STOP BOT
# ============================================

# From within tmux
Ctrl+C

# Kill all Python processes
killall python3

# Kill specific process
pkill -f "Tiktok_with_cookies_V2.py"

# ============================================
# 🧹 CLEANUP LOGS
# ============================================

# Clear main log
> bot.log

# Clear all logs
rm -f bot*.log

# Archive logs
tar -czf bot_logs_$(date +%Y%m%d).tar.gz bot*.log
rm -f bot*.log

# ============================================
# 🔍 DEBUGGING
# ============================================

# Check if bot is running
ps aux | grep "Tiktok_with_cookies_V2.py"
pgrep -f "Tiktok_with_cookies_V2.py"

# Check Chromium
chromium-browser --version
which chromedriver

# Check memory usage
free -h
ps aux --sort=-%mem | head -5

# Check disk space
df -h

# ============================================
# 📈 STATISTICS
# ============================================

# Total lines in log
wc -l bot*.log

# Log size
ls -lh bot*.log

# Last crash time
tail -1 bot_crashes.log

# ============================================
# 🔧 MAINTENANCE
# ============================================

# Update script (if new version)
git pull origin main

# Check permissions
ls -l run-bot-safe.sh

# Make executable
chmod +x run-bot-safe.sh

# ============================================
# 📱 TERMUX SPECIFIC
# ============================================

# Login proot
proot-distro login ubuntu

# Check Python
python3 --version
which python3

# Activate venv (if used)
source venv/bin/activate

# Install/update packages
pip install -r requirements.txt

# ============================================
