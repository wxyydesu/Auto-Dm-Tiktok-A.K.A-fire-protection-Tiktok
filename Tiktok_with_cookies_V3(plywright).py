from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

def send_dm_playwright(username, message):
    """Kirim DM ke username dengan screenshot setiap langkah"""
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - PLAYWRIGHT")
    print("="*60)
    print(f"Target : @{username}")
    print(f"Pesan  : {message}")
    print(f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    with sync_playwright() as p:
        print("\n> Launching browser...")
        browser = p.chromium.launch(
            headless=True,  # Bisa diubah ke False untuk debugging
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-setuid-sandbox'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # Set timeout
        page.set_default_timeout(60000)
        
        # --- Langkah 1: Load cookies ---
        print("> Memuat cookies...")
        with open('cookies_backup.json') as f:
            cookies = json.load(f)
            context.add_cookies(cookies)
        print(f"  Loaded {len(cookies)} cookies")
        
        # --- Langkah 2: Buka TikTok homepage ---
        print("\n> Langkah 1: Membuka TikTok homepage...")
        page.goto('https://www.tiktok.com', timeout=60000)
        page.wait_for_load_state('networkidle')
        screenshot = f"01_homepage_{int(time.time())}.png"
        page.screenshot(path=screenshot)
        print(f"  📸 Screenshot: {screenshot}")
        print(f"  URL: {page.url}")
        time.sleep(2)
        
        # --- Langkah 3: Buka profile target ---
        print(f"\n> Langkah 2: Membuka profile @{username}...")
        page.goto(f'https://www.tiktok.com/@{username}', timeout=60000)
        page.wait_for_load_state('networkidle')
        screenshot = f"02_profile_{username}_{int(time.time())}.png"
        page.screenshot(path=screenshot)
        print(f"  📸 Screenshot: {screenshot}")
        print(f"  URL: {page.url}")
        time.sleep(3)
        
        # --- Langkah 4: Cek apakah ada tombol Message ---
        print("\n> Langkah 3: Mencari tombol Message...")
        
        # Cek berbagai kemungkinan selector
        message_selectors = [
            'button:has-text("Message")',
            'button:has-text("Pesan")',
            'div[data-e2e="message-btn"]',
            'button[aria-label="Message"]',
            'div:has-text("Message") >> button'
        ]
        
        msg_button = None
        for selector in message_selectors:
            try:
                msg_button = page.locator(selector).first
                if msg_button.is_visible(timeout=3000):
                    print(f"  ✓ Tombol Message ditemukan dengan selector: {selector}")
                    break
            except:
                continue
        
        if msg_button and msg_button.is_visible():
            # Klik tombol Message
            msg_button.click()
            print("  ✓ Tombol Message diklik!")
            time.sleep(2)
            
            # Screenshot setelah klik
            screenshot = f"03_after_click_msg_{int(time.time())}.png"
            page.screenshot(path=screenshot)
            print(f"  📸 Screenshot: {screenshot}")
        else:
            print("  ✗ Tombol Message tidak ditemukan!")
            screenshot = f"error_no_message_{int(time.time())}.png"
            page.screenshot(path=screenshot)
            print(f"  📸 Screenshot error: {screenshot}")
            browser.close()
            return False
        
        # --- Langkah 5: Cari textarea untuk pesan ---
        print("\n> Langkah 4: Mencari textarea...")
        
        textarea_selectors = [
            'div[contenteditable="true"]',
            'textarea[placeholder*="message"]',
            'textarea[placeholder*="Message"]',
            'div[role="textbox"]'
        ]
        
        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = page.locator(selector).first
                if textarea.is_visible(timeout=3000):
                    print(f"  ✓ Textarea ditemukan dengan selector: {selector}")
                    break
            except:
                continue
        
        if textarea and textarea.is_visible():
            # Klik textarea
            textarea.click()
            time.sleep(1)
            
            # Screenshot sebelum mengetik
            screenshot = f"04_before_type_{int(time.time())}.png"
            page.screenshot(path=screenshot)
            print(f"  📸 Screenshot: {screenshot}")
            
            # --- Langkah 6: Ketik pesan ---
            print(f"\n> Langkah 5: Mengetik pesan...")
            textarea.fill(message)
            print(f"  Pesan: {message}")
            time.sleep(1)
            
            # Screenshot setelah mengetik
            screenshot = f"05_after_type_{int(time.time())}.png"
            page.screenshot(path=screenshot)
            print(f"  📸 Screenshot: {screenshot}")
            
            # --- Langkah 7: Kirim pesan ---
            print("\n> Langkah 6: Mengirim pesan...")
            page.keyboard.press('Enter')
            time.sleep(2)
            
            # Screenshot bukti terkirim
            screenshot = f"06_sent_{username}_{int(time.time())}.png"
            page.screenshot(path=screenshot)
            print(f"  📸 Screenshot bukti: {screenshot}")
            
            print(f"\n✓✓✓ PESAN BERHASIL TERKIRIM! ✓✓✓")
            print(f"  Target: @{username}")
            print(f"  Pesan: {message}")
            
            # --- Log ke file ---
            with open('dm_log.txt', 'a') as f:
                f.write(f"[{datetime.now()}] ✓ DM ke @{username}: {message}\n")
            
            browser.close()
            return True
        else:
            print("  ✗ Textarea tidak ditemukan!")
            screenshot = f"error_no_textarea_{int(time.time())}.png"
            page.screenshot(path=screenshot)
            print(f"  📸 Screenshot error: {screenshot}")
            browser.close()
            return False

def send_with_retry(username, message, max_retry=3):
    """Kirim DM dengan retry jika gagal"""
    
    for attempt in range(max_retry):
        print(f"\n{'='*60}")
        print(f"Percobaan ke-{attempt + 1} dari {max_retry}")
        print(f"{'='*60}")
        
        try:
            success = send_dm_playwright(username, message)
            if success:
                print(f"\n✓ Sukses pada percobaan ke-{attempt + 1}")
                return True
            else:
                print(f"\n✗ Gagal pada percobaan ke-{attempt + 1}")
                if attempt < max_retry - 1:
                    print("  Menunggu 10 detik sebelum retry...")
                    time.sleep(10)
        except Exception as e:
            print(f"\n✗ Error pada percobaan ke-{attempt + 1}: {e}")
            if attempt < max_retry - 1:
                print("  Menunggu 10 detik sebelum retry...")
                time.sleep(10)
    
    print(f"\n✗ Gagal setelah {max_retry} percobaan")
    return False

# Main program
if __name__ == "__main__":
    import os
    os.system('clear')
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - PLAYWRIGHT")
    print("="*60)
    
    # Input target
    username = input("\n> Username target (tanpa @): ").strip()
    if not username:
        print("Username tidak boleh kosong!")
        exit()
    
    pesan = input("> Pesan: ").strip()
    if not pesan:
        pesan = "Halo!"
    
    # Pilihan send mode
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
            send_with_retry(username, pesan, max_retry=3)
    else:
        print("Pilihan tidak valid")