import requests
import json
import time
import re
import os
import schedule
import threading
import random
from datetime import datetime

os.environ['DISPLAY'] = ':99'
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TikTokAutoDM:
    def __init__(self):
        self.driver = None
        self.cookies = None
        self.scheduled_jobs = []
        self.schedule_type = None
        self.schedule_hour = None
        self.schedule_minute = None
        self.schedule_day = None
        
    def load_cookies_from_file(self, filename='cookies_backup.json'):
        """Load cookies dari file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.cookies = json.load(f)
            print(f"> Load {len(self.cookies)} cookies dari {filename} <")
            return True
        except FileNotFoundError:
            print(f"File {filename} tidak ditemukan!")
            print("   Jalankan script dengan pilihan 1 dulu untuk membuat file cookies")
            return False
        except json.JSONDecodeError:
            print(f"File {filename} corrupt")
            return False
    
    def get_cookies_from_input(self):
        """Minta user paste cookies dari EditThisCookie"""
        print("\n" + "="*60)
        print("  PANDAUAN EXPORT COOKIES DARI EDITTHISCOOKIE")
        print("="*60)
        print("1. Buka TikTok di Chrome dan login")
        print("2. Klik icon EditThisCookie V3 di extension")
        print("3. Klik tombol 'Export' (icon panah keluar)")
        print("4. Klik 'Copy as JSON'")
        print("5. Paste di bawah ini")
        print("="*60)
        
        print("\n> Paste cookies JSON di sini (ketik 'done' jika sudah paste) <")
        print("-"*60)
        
        lines = []
        while True:
            line = input()
            if line.lower() == 'done':
                break
            lines.append(line)
        
        cookies_text = '\n'.join(lines)
        
        try:
            self.cookies = json.loads(cookies_text)
            print(f"\n> Berhasil load {len(self.cookies)} cookies!")
            
            # Simpan ke file
            with open('cookies_backup.json', 'w') as f:
                json.dump(self.cookies, f, indent=2)
            print("> Cookies disimpan di cookies_backup.json")
            print("   Next time bisa langsung pakai file ini!")
            
            return True
        except json.JSONDecodeError as e:
            print(f"\n Format JSON error: {e}")
            return False
    
    def wait_for_textarea(self, driver, timeout=15):
        """Optimasi pencarian textarea berdasarkan struktur HTML TikTok dengan robust waiting"""
        print("> Mencari textarea...")
        
        textarea_selectors = [
            "//div[@contenteditable='true' and @role='textbox']",
            "//div[contains(@class, 'public-DraftEditor-content') and @contenteditable='true']",
            "//div[@aria-label='Send a message...' and @contenteditable='true']",
            "//textarea[@placeholder='Send a message...']",
            "//textarea[@aria-label='Message']",
            "//textarea",
            "//div[contains(@class, 'DraftEditor-editorContainer')]//div[@contenteditable='true']"
        ]
        
        for selector in textarea_selectors:
            try:
                print(f"> Mencoba selector: {selector[:50]}...")
                element = WebDriverWait(driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, selector))
                )
                print(f"> Textarea ditemukan! Selector: {selector[:50]}...")
                return element
            except:
                continue
        
        print("> Textarea tidak ditemukan setelah search semua selector!")
        return None
    
    def create_webdriver_termux(self):
        """Create WebDriver specifically for Termux environment"""
        # Path untuk Termux
        chromium_paths = [
            "/data/data/com.termux/files/usr/bin/chromium-browser",
            "/data/data/com.termux/files/usr/bin/chromium"
        ]
        
        chromedriver_paths = [
            "/data/data/com.termux/files/usr/bin/chromedriver",
            "/data/data/com.termux/files/usr/bin/chromedriver.exe"
        ]
        
        chromium_path = None
        for path in chromium_paths:
            if os.path.exists(path):
                chromium_path = path
                break
        
        chromedriver_path = None
        for path in chromedriver_paths:
            if os.path.exists(path):
                chromedriver_path = path
                break
        
        if not chromium_path or not chromedriver_path:
            print("❌ Chromium atau ChromeDriver tidak ditemukan di Termux!")
            print("\nInstall dengan perintah:")
            print("  pkg update && pkg upgrade")
            print("  pkg install chromium chromedriver")
            return None
        
        print(f"✓ Chromium ditemukan: {chromium_path}")
        print(f"✓ ChromeDriver ditemukan: {chromedriver_path}")
        
        # Setup Chrome options untuk Termux
        chrome_options = Options()
        chrome_options.binary_location = chromium_path
        
        # Critical options untuk Termux/Proot
        chrome_options.add_argument("--headless=new")  # Wajib untuk Termux
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Memory optimization
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=512")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # User data dir di /tmp (bukan di /root)
        temp_dir = f"/tmp/chrome-profile-{random.randint(1000, 9999)}"
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        # Window size
        chrome_options.add_argument("--window-size=1280,720")
        
        # Disable features yang bikin crash
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Kurangi memory
        chrome_options.add_argument("--disable-javascript")  # Optional, bisa diaktifkan jika perlu
        
        # Logging untuk debug
        chrome_options.add_argument("--log-level=3")  # ERROR only
        
        # Service dengan timeout yang lebih panjang
        service = Service(
            chromedriver_path,
            service_log_path="/tmp/chromedriver.log"
        )
        
        try:
            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            return driver
        except Exception as e:
            print(f"❌ Gagal membuat WebDriver: {e}")
            return None
    
    def send_dm(self, username, message):
        """Kirim DM ke username tertentu"""
        
        print("\n" + "="*60)
        print("  MENGIRIM DM VIA BROWSER")
        print("="*60)
        print(f"Target : @{username}")
        print(f"Pesan  : {message}")
        print(f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        print("\n> Membuka browser...")
        
        # Create WebDriver khusus Termux
        driver = self.create_webdriver_termux()
        if driver is None:
            print("\n❌ Gagal membuat WebDriver untuk Termux!")
            return False
        
        try:
            # Buka TikTok dengan timeout
            print("> Membuka TikTok...")
            driver.get("https://www.tiktok.com")
            time.sleep(5)
            
            # Apply cookies
            print("> Memuat cookies...")
            for cookie in self.cookies:
                try:
                    clean_cookie = {
                        'name': cookie.get('name'),
                        'value': cookie.get('value'),
                        'domain': '.tiktok.com',
                        'path': '/'
                    }
                    if cookie.get('secure'):
                        clean_cookie['secure'] = True
                    
                    driver.add_cookie(clean_cookie)
                except:
                    pass
            
            print("> Cookies loaded")
            driver.refresh()
            time.sleep(5)
            
            # Buka profile target
            print(f"\n> Membuka profile @{username}...")
            driver.get(f"https://www.tiktok.com/@{username}")
            time.sleep(5)
            
            # Screenshot untuk debug
            driver.save_screenshot("01_profile_page.png")
            print("📸 Screenshot: 01_profile_page.png")
            
            # Cari tombol Message
            try:
                print("> Mencari tombol Message...")
                msg_selectors = [
                    "//div[@data-testid='tux-web-text' and text()='Message']",
                    "//button[contains(@class, 'send-message')]",
                    "//div[contains(text(), 'Message')]"
                ]
                
                msg_btn = None
                for selector in msg_selectors:
                    try:
                        msg_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"> Tombol Message ditemukan")
                        break
                    except:
                        continue
                
                if msg_btn:
                    driver.execute_script("arguments[0].click();", msg_btn)
                    print("> Tombol Message diklik!")
                    time.sleep(3)
                else:
                    print("> Tombol Message tidak ditemukan!")
                    driver.save_screenshot("02_no_message_button.png")
                    return False
                
                # Cari textarea
                textarea = self.wait_for_textarea(driver)
                
                if textarea:
                    # Scroll dan klik textarea
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea)
                    time.sleep(1)
                    
                    try:
                        textarea.click()
                    except:
                        driver.execute_script("arguments[0].click();", textarea)
                    time.sleep(1)
                    
                    # Kirim pesan
                    for char in message:
                        textarea.send_keys(char)
                        time.sleep(random.uniform(0.03, 0.08))
                    
                    time.sleep(0.5)
                    textarea.send_keys(Keys.RETURN)
                    
                    print(f"\n✓✓✓ PESAN BERHASIL TERKIRIM! ✓✓✓")
                    print(f"   Target: @{username}")
                    print(f"   Pesan: {message}")
                    print(f"   Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    time.sleep(2)
                    
                    # Screenshot bukti
                    screenshot = f"dm_sent_{username}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    driver.save_screenshot(screenshot)
                    print(f"📸 Screenshot bukti: {screenshot}")
                    
                    # Log pengiriman
                    with open('dm_log.txt', 'a', encoding='utf-8') as log:
                        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DM ke @{username}: {message}\n")
                    
                    driver.quit()
                    return True
                else:
                    print("> Textarea tidak ditemukan!")
                    driver.save_screenshot("03_no_textarea.png")
                    return False
                
            except Exception as e:
                print(f"> Error: {e}")
                driver.save_screenshot("04_error.png")
                return False
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"> Error utama: {e}")
            if driver:
                driver.quit()
            return False
    
    def run_scheduled_dm(self, username, message):
        """Wrapper untuk schedule dengan retry logic"""
        print(f"\n>>> Menjalankan DM terjadwal untuk @{username} <<<")
        
        retry = 0
        max_retry = 3
        
        while retry < max_retry:
            try:
                success = self.send_dm(username, message)
                
                if success:
                    print("\n✓ DM berhasil terkirim!")
                    break
                    
            except Exception as e:
                print(f"\n❌ Error: {e}")
            
            retry += 1
            if retry < max_retry:
                print(f"\n> Retry {retry}/{max_retry} dalam 15 detik...")
                time.sleep(15)
            else:
                print(f"\n❌ Gagal setelah {max_retry} percobaan")
        
        if self.schedule_type == "daily":
            print(f"\n> Menunggu jadwal berikutnya setiap hari pukul {self.schedule_hour:02d}:{self.schedule_minute:02d}")
        elif self.schedule_type == "weekly":
            day_names = {0:"Senin", 1:"Selasa", 2:"Rabu", 3:"Kamis", 4:"Jumat", 5:"Sabtu", 6:"Minggu"}
            print(f"\n> Menunggu jadwal berikutnya setiap {day_names.get(self.schedule_day, 'Minggu')} pukul {self.schedule_hour:02d}:{self.schedule_minute:02d}")
    
    def schedule_daily_dm(self, username, message, hour, minute):
        """Schedule DM setiap hari pada jam tertentu"""
        self.schedule_type = "daily"
        self.schedule_hour = hour
        self.schedule_minute = minute
        schedule_time = f"{hour:02d}:{minute:02d}"
        schedule.every().day.at(schedule_time).do(self.run_scheduled_dm, username, message)
        self.scheduled_jobs.append(schedule_time)
        print(f"> DM terjadwal setiap hari pukul {schedule_time}")
        return True
    
    def schedule_weekly_dm(self, username, message, day, hour, minute):
        """Schedule DM setiap minggu pada hari dan jam tertentu"""
        self.schedule_type = "weekly"
        self.schedule_hour = hour
        self.schedule_minute = minute
        self.schedule_day = day
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule_time = f"{hour:02d}:{minute:02d}"
        
        if day == 0:
            schedule.every().monday.at(schedule_time).do(self.run_scheduled_dm, username, message)
        elif day == 1:
            schedule.every().tuesday.at(schedule_time).do(self.run_scheduled_dm, username, message)
        elif day == 2:
            schedule.every().wednesday.at(schedule_time).do(self.run_scheduled_dm, username, message)
        elif day == 3:
            schedule.every().thursday.at(schedule_time).do(self.run_scheduled_dm, username, message)
        elif day == 4:
            schedule.every().friday.at(schedule_time).do(self.run_scheduled_dm, username, message)
        elif day == 5:
            schedule.every().saturday.at(schedule_time).do(self.run_scheduled_dm, username, message)
        elif day == 6:
            schedule.every().sunday.at(schedule_time).do(self.run_scheduled_dm, username, message)
        
        self.scheduled_jobs.append(f"{day_names[day]} {schedule_time}")
        print(f"> DM terjadwal setiap {day_names[day]} pukul {schedule_time}")
        return True
    
    def stop_schedule(self):
        """Stop semua schedule"""
        schedule.clear()
        self.scheduled_jobs = []
        self.schedule_type = None
        self.schedule_hour = None
        self.schedule_minute = None
        self.schedule_day = None
        print("> Semua jadwal dihentikan")

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def run_schedule_loop():
    """Loop untuk menjalankan schedule"""
    print("\n> Schedule loop berjalan...\n")
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    clear_screen()
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - TERMUX VERSION")
    print("="*60)
    
    bot = TikTokAutoDM()
    
    # Cek apakah ada file cookies
    if not os.path.exists('cookies_backup.json'):
        print("\n> BELUM ADA COOKIES!")
        print("   Harus login dulu (hanya sekali)\n")
        
        if bot.get_cookies_from_input():
            print("\n> Cookies saved! Silakan jalankan ulang script.")
        else:
            print("\n> Gagal menyimpan cookies!")
        return
    
    # Load cookies
    if not bot.load_cookies_from_file():
        return
    
    # Input target dan pesan
    print("\n" + "="*60)
    print("  INPUT DATA")
    print("="*60)
    
    # Input username target
    while True:
        username = input("\n> Username target (tanpa @): ").strip()
        if username:
            break
        print("   Username tidak boleh kosong!")
    
    # Input pesan
    pesan = input("\n> Pesan yang akan dikirim: ").strip()
    if not pesan:
        pesan = "Halo!"
    
    # Pilihan kirim sekarang atau schedule
    print("\n" + "="*60)
    print("  PILIH METODE PENGIRIMAN")
    print("="*60)
    print("1. Kirim sekarang")
    print("2. Jadwalkan pengiriman")
    print("="*60)
    
    pilihan = input("\nPilih (1/2): ").strip()
    
    if pilihan == "1":
        # Kirim sekarang
        print("\n" + "="*60)
        print("  KONFIRMASI")
        print("="*60)
        print(f"Target : @{username}")
        print(f"Pesan  : {pesan}")
        print("="*60)
        
        konfirmasi = input("\nKirim DM? (y/n): ").strip().lower()
        
        if konfirmasi == 'y':
            success = bot.send_dm(username, pesan)
            
            if success:
                print("\n✓ Pengiriman DM selesai!")
            else:
                print("\n❌ Pengiriman DM gagal!")
        else:
            print("> Dibatalkan")
    
    elif pilihan == "2":
        # Jadwalkan pengiriman
        print("\n" + "="*60)
        print("  JADWALKAN PENGIRIMAN")
        print("="*60)
        print("1. Setiap hari (daily)")
        print("2. Setiap minggu (weekly)")
        print("="*60)
        
        jadwal_type = input("\nPilih (1/2): ").strip()
        
        if jadwal_type == "1":
            # Daily schedule
            while True:
                try:
                    jam = int(input("\nJam (0-23): ").strip())
                    if 0 <= jam <= 23:
                        break
                    print("   Jam harus antara 0-23")
                except:
                    print("   Masukkan angka yang valid")
            
            while True:
                try:
                    menit = int(input("Menit (0-59): ").strip())
                    if 0 <= menit <= 59:
                        break
                    print("   Menit harus antara 0-59")
                except:
                    print("   Masukkan angka yang valid")
            
            print("\n" + "="*60)
            print("  KONFIRMASI JADWAL")
            print("="*60)
            print(f"Target    : @{username}")
            print(f"Pesan     : {pesan}")
            print(f"Jadwal    : Setiap hari pukul {jam:02d}:{menit:02d}")
            print("="*60)
            
            konfirmasi = input("\nAktifkan jadwal? (y/n): ").strip().lower()
            
            if konfirmasi == 'y':
                bot.schedule_daily_dm(username, pesan, jam, menit)
                print(f"\n> Jadwal aktif! DM akan dikirim setiap hari pukul {jam:02d}:{menit:02d}")
                print("> Script akan berjalan terus... Tekan Ctrl+C untuk berhenti")
                print("> " + "="*56)
                
                try:
                    run_schedule_loop()
                except KeyboardInterrupt:
                    print("\n\n> Script dihentikan oleh user")
                    bot.stop_schedule()
            else:
                print("> Dibatalkan")
        
        elif jadwal_type == "2":
            # Weekly schedule
            print("\nPilih hari:")
            print("1. Senin")
            print("2. Selasa")
            print("3. Rabu")
            print("4. Kamis")
            print("5. Jumat")
            print("6. Sabtu")
            print("7. Minggu")
            
            while True:
                try:
                    hari = int(input("\nPilih (1-7): ").strip())
                    if 1 <= hari <= 7:
                        break
                    print("   Pilihan harus 1-7")
                except:
                    print("   Masukkan angka yang valid")
            
            while True:
                try:
                    jam = int(input("\nJam (0-23): ").strip())
                    if 0 <= jam <= 23:
                        break
                    print("   Jam harus antara 0-23")
                except:
                    print("   Masukkan angka yang valid")
            
            while True:
                try:
                    menit = int(input("Menit (0-59): ").strip())
                    if 0 <= menit <= 59:
                        break
                    print("   Menit harus antara 0-59")
                except:
                    print("   Masukkan angka yang valid")
            
            day_map = {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6}
            day_names = {1:"Senin", 2:"Selasa", 3:"Rabu", 4:"Kamis", 5:"Jumat", 6:"Sabtu", 7:"Minggu"}
            
            print("\n" + "="*60)
            print("  KONFIRMASI JADWAL")
            print("="*60)
            print(f"Target    : @{username}")
            print(f"Pesan     : {pesan}")
            print(f"Jadwal    : Setiap {day_names[hari]} pukul {jam:02d}:{menit:02d}")
            print("="*60)
            
            konfirmasi = input("\nAktifkan jadwal? (y/n): ").strip().lower()
            
            if konfirmasi == 'y':
                bot.schedule_weekly_dm(username, pesan, day_map[hari], jam, menit)
                print(f"\n> Jadwal aktif! DM akan dikirim setiap {day_names[hari]} pukul {jam:02d}:{menit:02d}")
                print("> Script akan berjalan terus... Tekan Ctrl+C untuk berhenti")
                print("> " + "="*56)
                
                try:
                    run_schedule_loop()
                except KeyboardInterrupt:
                    print("\n\n> Script dihentikan oleh user")
                    bot.stop_schedule()
            else:
                print("> Dibatalkan")
        
        else:
            print("> Pilihan tidak valid")
    
    else:
        print("> Pilihan tidak valid")

if __name__ == "__main__":
    main()