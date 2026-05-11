#!/usr/bin/env python3
import os
import subprocess
import time
import signal
import sys
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def setup_xvfb():
    """Setup Xvfb otomatis jika belum running"""
    
    # Cek apakah Xvfb sudah berjalan
    result = subprocess.run(['pgrep', '-x', 'Xvfb'], capture_output=True)
    if result.returncode == 0:
        print("✓ Xvfb sudah berjalan")
        return True
    
    # Cek apakah Xvfb terinstall
    xvfb_path = "/data/data/com.termux/files/usr/bin/Xvfb"
    if not os.path.exists(xvfb_path):
        print("⚠️ Xvfb tidak ditemukan, install dengan:")
        print("   pkg install xorg-server-xvfb")
        return False
    
    # Jalankan Xvfb
    print("> Menjalankan Xvfb di background...")
    display_num = 99
    xvfb_process = subprocess.Popen(
        [xvfb_path, f":{display_num}", "-screen", "0", "1280x720x16"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    time.sleep(2)  # Beri waktu Xvfb startup
    
    # Set DISPLAY environment variable
    os.environ['DISPLAY'] = f":{display_num}"
    
    # Cek apakah berjalan
    result = subprocess.run(['pgrep', '-x', 'Xvfb'], capture_output=True)
    if result.returncode == 0:
        print(f"✓ Xvfb berjalan di display :{display_num}")
        return True
    else:
        print("✗ Gagal menjalankan Xvfb")
        return False

def kill_xvfb():
    """Matikan Xvfb (opsional)"""
    subprocess.run(['pkill', '-x', 'Xvfb'], capture_output=True)
    print("✓ Xvfb dimatikan")

def send_dm_playwright(username, message):
    """Kirim DM dengan screenshot setiap langkah"""
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - PLAYWRIGHT")
    print("="*60)
    print(f"Target : @{username}")
    print(f"Pesan  : {message}")
    print(f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Auto setup Xvfb
    if not setup_xvfb():
        print("❌ Xvfb setup gagal, exit...")
        return False
    
    try:
        with sync_playwright() as p:
            print("\n> Launching browser...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-setuid-sandbox',
                    '--disable-breakpad',
                    '--disable-crash-reporter'
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            page.set_default_timeout(60000)
            
            # --- Load cookies ---
            print("> Memuat cookies...")
            if not os.path.exists('cookies_backup.json'):
                print("✗ File cookies_backup.json tidak ditemukan!")
                return False
                
            with open('cookies_backup.json') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
            print(f"  Loaded {len(cookies)} cookies")
            
            # --- Buka TikTok ---
            print("\n> Membuka TikTok...")
            page.goto('https://www.tiktok.com', timeout=60000)
            page.wait_for_load_state('networkidle')
            page.screenshot(path="01_homepage.png")
            print("  📸 Screenshot: 01_homepage.png")
            time.sleep(2)
            
            # --- Buka profile ---
            print(f"\n> Membuka profile @{username}...")
            page.goto(f'https://www.tiktok.com/@{username}', timeout=60000)
            page.wait_for_load_state('networkidle')
            page.screenshot(path="02_profile.png")
            print("  📸 Screenshot: 02_profile.png")
            time.sleep(3)
            
            # --- Cari tombol Message ---
            print("\n> Mencari tombol Message...")
            message_selectors = [
                'button:has-text("Message")',
                'button:has-text("Pesan")',
                'div[data-e2e="message-btn"]',
                'button[aria-label="Message"]'
            ]
            
            msg_button = None
            for selector in message_selectors:
                try:
                    msg_button = page.locator(selector).first
                    if msg_button.is_visible(timeout=3000):
                        print(f"  ✓ Tombol Message ditemukan: {selector}")
                        break
                except:
                    continue
            
            if msg_button and msg_button.is_visible():
                msg_button.click()
                print("  ✓ Tombol Message diklik!")
                time.sleep(2)
                page.screenshot(path="03_after_click_msg.png")
                print("  📸 Screenshot: 03_after_click_msg.png")
            else:
                print("  ✗ Tombol Message tidak ditemukan!")
                page.screenshot(path="error_no_message.png")
                return False
            
            # --- Cari textarea ---
            print("\n> Mencari textarea...")
            textarea_selectors = [
                'div[contenteditable="true"]',
                'textarea[placeholder*="message"]',
                'div[role="textbox"]'
            ]
            
            textarea = None
            for selector in textarea_selectors:
                try:
                    textarea = page.locator(selector).first
                    if textarea.is_visible(timeout=3000):
                        print(f"  ✓ Textarea ditemukan: {selector}")
                        break
                except:
                    continue
            
            if textarea and textarea.is_visible():
                textarea.click()
                time.sleep(1)
                page.screenshot(path="04_before_type.png")
                print("  📸 Screenshot: 04_before_type.png")
                
                # --- Kirim pesan ---
                print(f"\n> Mengirim pesan...")
                textarea.fill(message)
                time.sleep(1)
                page.screenshot(path="05_after_type.png")
                print("  📸 Screenshot: 05_after_type.png")
                
                page.keyboard.press('Enter')
                time.sleep(2)
                
                # Screenshot bukti
                page.screenshot(path="06_sent.png")
                print("  📸 Screenshot bukti: 06_sent.png")
                
                print(f"\n✓✓✓ PESAN BERHASIL TERKIRIM! ✓✓✓")
                print(f"  Target: @{username}")
                print(f"  Pesan: {message}")
                
                # Log
                with open('dm_log.txt', 'a') as f:
                    f.write(f"[{datetime.now()}] ✓ DM ke @{username}: {message}\n")
                
                browser.close()
                return True
            else:
                print("  ✗ Textarea tidak ditemukan!")
                page.screenshot(path="error_no_textarea.png")
                return False
                
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    finally:
        # Optional: Matikan Xvfb setelah selesai (comment if you want to keep running)
        # kill_xvfb()
        pass

def send_with_retry(username, message, max_retry=3):
    """Kirim dengan retry"""
    
    for attempt in range(max_retry):
        print(f"\n📌 Percobaan ke-{attempt + 1} dari {max_retry}")
        
        success = send_dm_playwright(username, message)
        if success:
            print(f"\n✓ Sukses pada percobaan ke-{attempt + 1}")
            return True
        else:
            print(f"\n✗ Gagal pada percobaan ke-{attempt + 1}")
            if attempt < max_retry - 1:
                print("  Menunggu 10 detik sebelum retry...")
                time.sleep(10)
    
    print(f"\n✗ Gagal setelah {max_retry} percobaan")
    return False

def main():
    os.system('clear')
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - PLAYWRIGHT (AUTO XVFB)")
    print("="*60)
    print("\n📌 Script akan setup Xvfb otomatis!")
    print("="*60)
    
    # Cek cookies
    if not os.path.exists('cookies_backup.json'):
        print("\n⚠️ File cookies_backup.json tidak ditemukan!")
        print("\nCara membuat:")
        print("1. Install extension 'EditThisCookie' di Chrome PC")
        print("2. Login ke TikTok")
        print("3. Export cookies ke JSON")
        print("4. Simpan sebagai cookies_backup.json")
        return
    
    # Input target
    username = input("\n> Username target (tanpa @): ").strip()
    if not username:
        print("Username tidak boleh kosong!")
        return
    
    pesan = input("> Pesan: ").strip()
    if not pesan:
        pesan = "Halo!"
    
    # Pilihan
    print("\n1. Kirim sekarang")
    print("2. Kirim dengan retry (3x)")
    pilih = input("\nPilih (1/2): ")
    
    if pilih == "1":
        confirm = input(f"\nKirim ke @{username}? (y/n): ")
        if confirm.lower() == 'y':
            send_dm_playwright(username, pesan)
    elif pilih == "2":
        confirm = input(f"\nKirim ke @{username} dengan retry? (y/n): ")
        if confirm.lower() == 'y':
            send_with_retry(username, pesan)
    else:
        print("Pilihan tidak valid")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n> Dihentikan user")
        kill_xvfb()
    except Exception as e:
        print(f"\n> Error: {e}")