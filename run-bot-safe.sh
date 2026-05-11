#!/bin/bash

# TikTok Auto DM - Auto-Restart Wrapper Script
# Keeps bot running dengan auto-restart jika crash
# Usage: bash run-bot-safe.sh
# Or: tmux new-session -s tiktok-dm -d "bash run-bot-safe.sh"

set -u

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Config
BOT_SCRIPT="Tiktok_with_cookies_V2.py"
LOG_FILE="bot.log"
ERROR_LOG="bot_error.log"
CRASH_LOG="bot_crashes.log"
MAX_RESTARTS=999
RESTART_DELAY=5
CRASH_THRESHOLD=5
CRASH_TIME_WINDOW=60

# State variables
CRASH_COUNT=0
LAST_CRASH_TIME=0
TOTAL_RUNS=0
TOTAL_CRASHES=0

# Functions
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE" "$ERROR_LOG"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

check_environment() {
    print_status "Memeriksa environment..."
    
    if [ ! -f "$BOT_SCRIPT" ]; then
        print_error "Script $BOT_SCRIPT tidak ditemukan!"
        exit 1
    fi
    
    if [ ! -f "cookies_backup.json" ]; then
        print_warning "cookies_backup.json tidak ditemukan! Bot tidak bisa jalan!"
        print_status "Jalankan script dulu untuk setup cookies:"
        print_status "  python3 $BOT_SCRIPT"
        exit 1
    fi
    
    print_success "Environment OK"
}

run_bot() {
    local run_number=$((TOTAL_RUNS + 1))
    print_status "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_status "BOT RUN #$run_number"
    print_status "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    TOTAL_RUNS=$run_number
    
    # Run bot with output logging
    python3 -u "$BOT_SCRIPT" 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Bot selesai normal (exit code: 0)"
        CRASH_COUNT=0
    else
        print_error "Bot crash dengan exit code: $exit_code"
        log_crash "$exit_code"
        
        # Check crash frequency
        local current_time=$(date +%s)
        local time_since_last_crash=$((current_time - LAST_CRASH_TIME))
        
        if [ $time_since_last_crash -lt $CRASH_TIME_WINDOW ]; then
            CRASH_COUNT=$((CRASH_COUNT + 1))
        else
            CRASH_COUNT=1
        fi
        
        LAST_CRASH_TIME=$current_time
        TOTAL_CRASHES=$((TOTAL_CRASHES + 1))
        
        # Check if too many crashes
        if [ $CRASH_COUNT -ge $CRASH_THRESHOLD ]; then
            print_error "Terlalu banyak crash ($CRASH_COUNT dalam $CRASH_TIME_WINDOW detik)!"
            print_error "Mohon check log untuk debugging:"
            print_error "  tail -f $LOG_FILE"
            print_error "  tail -f $ERROR_LOG"
            exit 1
        fi
    fi
}

log_crash() {
    local exit_code=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] Crash #$TOTAL_CRASHES - Exit Code: $exit_code" >> "$CRASH_LOG"
}

show_stats() {
    echo ""
    print_status "═════════════════════════════════════════════"
    print_status "📊 BOT STATISTICS"
    print_status "═════════════════════════════════════════════"
    print_status "Total Runs: $TOTAL_RUNS"
    print_status "Total Crashes: $TOTAL_CRASHES"
    print_status "Crash Rate: $(echo "scale=2; $TOTAL_CRASHES * 100 / $TOTAL_RUNS" | bc)%"
    print_status "Log Files:"
    print_status "  - Main: $LOG_FILE"
    print_status "  - Errors: $ERROR_LOG"
    print_status "  - Crashes: $CRASH_LOG"
    print_status "═════════════════════════════════════════════"
    echo ""
}

# Main loop
main() {
    print_status "╔═════════════════════════════════════════════╗"
    print_status "║   TIKTOK AUTO DM - AUTO RESTART WRAPPER    ║"
    print_status "║         by WXYYDESU                         ║"
    print_status "╚═════════════════════════════════════════════╝"
    print_status ""
    
    check_environment
    
    print_status "Konfigurasi:"
    print_status "  - Script: $BOT_SCRIPT"
    print_status "  - Log: $LOG_FILE"
    print_status "  - Restart Delay: ${RESTART_DELAY}s"
    print_status "  - Max Restarts: $MAX_RESTARTS"
    print_status "  - Crash Threshold: $CRASH_THRESHOLD crashes per $CRASH_TIME_WINDOW seconds"
    print_status ""
    print_status "Tekan Ctrl+C untuk berhenti"
    print_status ""
    
    # Cleanup on exit
    trap 'print_status "Bot dihentikan oleh user"; show_stats; exit 0' SIGINT SIGTERM
    
    # Main loop
    while [ $TOTAL_RUNS -lt $MAX_RESTARTS ]; do
        run_bot
        
        if [ $TOTAL_RUNS -lt $MAX_RESTARTS ]; then
            print_warning "Restarting dalam $RESTART_DELAY detik..."
            sleep $RESTART_DELAY
        fi
    done
    
    print_error "Max restarts ($MAX_RESTARTS) tercapai!"
    show_stats
    exit 1
}

# Run main
main
