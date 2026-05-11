import json
import time
import os
import schedule
import random
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
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
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.cookies = json.load(f)
            print(f"> Load {len(self.cookies)} cookies dari {filename}")
            return True
        except:
            return False
    
    def get_cookies_from_input(self):
        print("\n" + "="*60)
        print("  EXPORT COOKIES DARI EDITTHISCOOKIE")
        print("="*60)
        print("1. Buka TikTok di Chrome/Firefox dan login")
        print("2. Klik icon EditThisCookie V3")
        print("3. Klik 'Export' -> 'Copy as JSON'")
        print("4. Paste di bawah ini (ketik 'done' selesai)")
        print("="*60)
        
        lines = []
        while True:
            line = input()
            if line.lower() == 'done':
                break
            lines.append(line)
        
        try:
            self.cookies = json.loads('\n'.join(lines))
            with open('cookies_backup.json', 'w') as f:
                json.dump(self.cookies, f, indent=2)
            print(f"✓ Berhasil simpan {len(self.cookies)} cookies")
            return True
        except:
            print("✗ Gagal parse JSON")
            return False
    
    def kill_firefox_processes(self):
        """Bersihkan proses Firefox yang hang"""
        os.system("pkill -9 -f firefox 2>/dev/null")
        os.system("pkill -9 -f geckodriver 2>/dev/null")
        time.sleep(2)
    
    def create_firefox_driver(self):
        """Buat Firefox driver untuk CLI Termux"""
        
        self.kill_firefox_processes()
        
        # Cek path Firefox
        firefox_path = "/data/data/com.termux/files/usr/bin/firefox"
        geckodriver_path = "/data/data/com.termux/files/usr/bin/geckodriver"
        
        if not os.path.exists(firefox_path):
            print("✗ Firefox tidak ditemukan!")
            print("  Install: pkg install firefox")
            return None
        
        if not os.path.exists(geckodriver_path):
            print("✗ Geckodriver tidak ditemukan!")
            print("  Install: pkg install geckodriver")
            return None
        
        print(f"✓ Firefox: {firefox_path}")
        print(f"✓ Geckodriver: {geckodriver_path}")
        
        # Options untuk headless di Termux
        options = Options()
        options.binary_location = firefox_path
        
        # Headless mode untuk CLI
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        
        # Disable GPU dan fitur berat
        options.set_preference("gfx.direct2d.disabled", True)
        options.set_preference("layers.acceleration.disabled", True)
        
        # Disable images untuk speed
        options.set_preference("permissions.default.image", 2)
        
        # Disable JavaScript (opsional, untuk testing)
        # options.set_preference("javascript.enabled", False)
        
        # Profile temporary
        profile_dir = f"/tmp/firefox_profile_{int(time.time())}"
        options.set_preference("browser.download.dir", profile_dir)
        
        # Log level minimal
        options.set_preference("webdriver.log.file", "/tmp/geckodriver.log")
        
        service = Service(geckodriver_path)
        
        try:
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_page_load_timeout(30)
            print("✓ Firefox driver berhasil dibuat")
            return driver
        except Exception as e:
            print(f"✗ Error membuat driver: {e}")
            return None
    
    def send_dm(self, username, message):
        print("\n" + "="*60)
        print("  MENGIRIM DM VIA FIREFOX (HEADLESS)")
        print("="*60)
        print(f"Target : @{username}")
        print(f"Pesan  : {message}")
        print(f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        driver = self.create_firefox_driver()
        if not driver:
            return False
        
        try:
            # Buka TikTok
            print("> Membuka TikTok...")
            driver.get("https://www.tiktok.com")
            
            # Tunggu load
            time.sleep(5)
            print(f"  URL: {driver.current_url}")
            
            # Load cookies
            print("> Memuat cookies...")
            for cookie in self.cookies:
                try:
                    # Format cookie untuk Firefox
                    cookie_dict = {
                        'name': cookie.get('name'),
                        'value': cookie.get('value'),
                        'domain': '.tiktok.com',
                        'path': '/'
                    }
                    if cookie.get('secure'):
                        cookie_dict['secure'] = True
                    if cookie.get('expiry'):
                        cookie_dict['expiry'] = cookie['expiry']
                    
                    driver.add_cookie(cookie_dict)
                except Exception as e:
                    pass
            
            print("> Cookies loaded, refresh...")
            driver.refresh()
            time.sleep(5)
            
            # Buka profile target
            print(f"> Buka profile @{username}...")
            driver.get(f"https://www.tiktok.com/@{username}")
            time.sleep(5)
            
            # Screenshot debug
            try:
                driver.save_screenshot("debug_profile.png")
                print("  Screenshot: debug_profile.png")
            except:
                pass
            
            # Cari tombol Message
            print("> Mencari tombol Message...")
            try:
                # Wait untuk tombol Message
                msg_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Message')]"))
                )
                msg_button.click()
                print("✓ Tombol Message diklik!")
            except:
                # Coba selector lain
                try:
                    msg_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Message')]"))
                    )
                    driver.execute_script("arguments[0].click();", msg_button)
                    print("✓ Tombol Message diklik (via JS)!")
                except:
                    print("✗ Tombol Message tidak ditemukan!")
                    driver.save_screenshot("error_no_message.png")
                    return False
            
            time.sleep(3)
            
            # Cari textarea
            print("> Mencari textarea...")
            textarea_selectors = [
                "//div[@contenteditable='true']",
                "//textarea[@placeholder='Send a message...']",
                "//textarea"
            ]
            
            textarea = None
            for selector in textarea_selectors:
                try:
                    textarea = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if textarea and textarea.is_displayed():
                        print(f"✓ Textarea ditemukan")
                        break
                except:
                    continue
            
            if textarea:
                # Scroll dan klik textarea
                driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
                time.sleep(1)
                textarea.click()
                time.sleep(1)
                
                # Kirim pesan
                print("> Mengirim pesan...")
                for char in message:
                    textarea.send_keys(char)
                    time.sleep(random.uniform(0.03, 0.08))
                
                time.sleep(0.5)
                textarea.send_keys(Keys.RETURN)
                
                print(f"\n✓✓✓ PESAN BERHASIL TERKIRIM! ✓✓✓")
                print(f"   Target: @{username}")
                print(f"   Pesan: {message}")
                
                # Screenshot bukti
                screenshot = f"dm_sent_{username}_{int(time.time())}.png"
                driver.save_screenshot(screenshot)
                print(f"  Screenshot: {screenshot}")
                
                # Log
                with open('dm_log.txt', 'a') as f:
                    f.write(f"[{datetime.now()}] DM ke @{username}: {message}\n")
                
                driver.quit()
                self.kill_firefox_processes()
                return True
            else:
                print("✗ Textarea tidak ditemukan!")
                driver.save_screenshot("error_no_textarea.png")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            try:
                driver.save_screenshot("error.png")
            except:
                pass
            return False
        finally:
            try:
                driver.quit()
            except:
                pass
            self.kill_firefox_processes()
    
    def schedule_daily_dm(self, username, message, hour, minute):
        self.schedule_type = "daily"
        self.schedule_hour = hour
        self.schedule_minute = minute
        schedule_time = f"{hour:02d}:{minute:02d}"
        schedule.every().day.at(schedule_time).do(self.run_scheduled_dm, username, message)
        print(f"✓ DM terjadwal setiap hari pukul {schedule_time}")
    
    def run_scheduled_dm(self, username, message):
        print(f"\n>>> Menjalankan DM terjadwal untuk @{username} <<<")
        
        # Retry logic
        max_retry = 3
        for retry in range(max_retry):
            try:
                success = self.send_dm(username, message)
                if success:
                    print(f"\n✓ DM berhasil terkirim!")
                    break
                else:
                    print(f"\n⚠️ Retry {retry + 1}/{max_retry}...")
                    time.sleep(10)
            except Exception as e:
                print(f"✗ Error: {e}")
                if retry < max_retry - 1:
                    time.sleep(10)

def run_schedule_loop():
    print("\n⏰ Schedule loop berjalan...\n")
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    os.system('clear')
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - FIREFOX (TERMUX)")
    print("="*60)
    
    bot = TikTokAutoDM()
    
    if not os.path.exists('cookies_backup.json'):
        print("\n⚠️ BELUM ADA COOKIES!")
        print("   Ambil cookies dari browser PC/laptop")
        print("   Extension: EditThisCookie\n")
        
        if bot.get_cookies_from_input():
            print("\n✓ Cookies saved! Jalankan ulang script.")
        return
    
    bot.load_cookies_from_file()
    
    username = input("\n> Username target (tanpa @): ").strip()
    pesan = input("> Pesan: ").strip()
    if not pesan:
        pesan = "Halo!"
    
    print("\n1. Kirim sekarang")
    print("2. Kirim terjadwal")
    pilih = input("\nPilih (1/2): ")
    
    if pilih == "1":
        confirm = input(f"\nKirim ke @{username}? (y/n): ")
        if confirm.lower() == 'y':
            success = bot.send_dm(username, pesan)
            if success:
                print("\n✓ Pengiriman selesai!")
            else:
                print("\n✗ Pengiriman gagal!")
    elif pilih == "2":
        jam = int(input("Jam (0-23): "))
        menit = int(input("Menit (0-59): "))
        bot.schedule_daily_dm(username, pesan, jam, menit)
        print("\n⏰ Menunggu jadwal... (Ctrl+C untuk stop)")
        try:
            run_schedule_loop()
        except KeyboardInterrupt:
            print("\n\n> Script dihentikan")
    else:
        print("Pilihan tidak valid")

if __name__ == "__main__":
    main()