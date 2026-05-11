import requests
import json
import time
import os
import schedule
import random
import subprocess
from datetime import datetime

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
        print("1. Buka TikTok di Chrome PC dan login")
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
    
    def kill_chrome_processes(self):
        """Bersihkan proses Chrome yang hang"""
        os.system("pkill -9 -f chromium 2>/dev/null")
        os.system("pkill -9 -f chromedriver 2>/dev/null")
        time.sleep(2)
    
    def create_chrome_driver(self):
        """Buat Chrome driver untuk CLI Termux"""
        
        self.kill_chrome_processes()
        
        # Cek path
        chrome_path = "/data/data/com.termux/files/usr/bin/chromium-browser"
        if not os.path.exists(chrome_path):
            chrome_path = "/data/data/com.termux/files/usr/bin/chromium"
        
        chromedriver_path = "/data/data/com.termux/files/usr/bin/chromedriver"
        
        if not os.path.exists(chrome_path) or not os.path.exists(chromedriver_path):
            print("✗ Install dulu:")
            print("   pkg install chromium chromedriver")
            return None
        
        print(f"✓ Chrome: {chrome_path}")
        print(f"✓ ChromeDriver: {chromedriver_path}")
        
        # Options untuk headless CLI
        options = Options()
        options.binary_location = chrome_path
        
        # Headless wajib untuk CLI
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        
        # Memory optimization CRITICAL
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=256")
        options.add_argument("--js-flags=--max-old-space-size=256")
        
        # Disable fitur yang berat
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")  # Matikan JS untuk testing
        
        # Profile di /tmp
        profile_dir = f"/tmp/chrome_headless_{int(time.time())}"
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--log-level=3")
        
        # Remote debugging
        options.add_argument("--remote-debugging-port=9222")
        
        # Environment variables
        os.environ['TMPDIR'] = '/tmp'
        os.environ['DISPLAY'] = ':99'  # Virtual display
        
        service = Service(chromedriver_path)
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def send_dm(self, username, message):
        print("\n" + "="*60)
        print("  MENGIRIM DM VIA BROWSER (HEADLESS)")
        print("="*60)
        print(f"Target : @{username}")
        print(f"Pesan  : {message}")
        print(f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        driver = self.create_chrome_driver()
        if not driver:
            return False
        
        try:
            # Buka TikTok
            print("> Membuka TikTok...")
            driver.get("https://www.tiktok.com")
            
            # Tunggu load
            for i in range(10):
                if "tiktok" in driver.current_url.lower():
                    break
                time.sleep(1)
            
            print(f"  URL: {driver.current_url}")
            time.sleep(3)
            
            # Load cookies
            print("> Memuat cookies...")
            for cookie in self.cookies:
                try:
                    cookie['domain'] = '.tiktok.com'
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    driver.add_cookie(cookie)
                except:
                    pass
            
            driver.refresh()
            time.sleep(5)
            
            # Buka profile target
            print(f"> Buka profile @{username}...")
            driver.get(f"https://www.tiktok.com/@{username}")
            time.sleep(5)
            
            # Screenshot debug
            driver.save_screenshot("debug_profile.png")
            print("  Screenshot: debug_profile.png")
            
            # Cari tombol Message via JS
            print("> Mencari tombol Message...")
            js_find_msg = """
            function findMessageButton() {
                // Cari button
                let buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.innerText === 'Message' || btn.textContent.includes('Message')) {
                        btn.click();
                        return true;
                    }
                }
                
                // Cari div dengan role button
                let divs = document.querySelectorAll('div[role="button"]');
                for (let div of divs) {
                    if (div.innerText === 'Message' || div.textContent.includes('Message')) {
                        div.click();
                        return true;
                    }
                }
                return false;
            }
            return findMessageButton();
            """
            
            msg_clicked = driver.execute_script(js_find_msg)
            
            if not msg_clicked:
                print("✗ Tombol Message tidak ditemukan!")
                driver.save_screenshot("error_no_message.png")
                return False
            
            print("✓ Tombol Message diklik!")
            time.sleep(3)
            
            # Cari textarea
            print("> Mencari textarea...")
            js_find_textarea = """
            function findTextarea() {
                // Cari div contenteditable
                let editors = document.querySelectorAll('div[contenteditable="true"]');
                for (let editor of editors) {
                    if (editor.offsetParent !== null) {
                        editor.click();
                        editor.focus();
                        return editor;
                    }
                }
                
                // Cari textarea biasa
                let textareas = document.querySelectorAll('textarea');
                for (let ta of textareas) {
                    if (ta.offsetParent !== null) {
                        ta.click();
                        ta.focus();
                        return ta;
                    }
                }
                return null;
            }
            return findTextarea();
            """
            
            textarea = driver.execute_script(js_find_textarea)
            
            if textarea:
                print("✓ Textarea ditemukan!")
                
                # Kirim pesan
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
                self.kill_chrome_processes()
                return True
            else:
                print("✗ Textarea tidak ditemukan!")
                driver.save_screenshot("error_no_textarea.png")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            driver.save_screenshot("error.png")
            return False
        finally:
            try:
                driver.quit()
            except:
                pass
            self.kill_chrome_processes()
    
    def schedule_daily_dm(self, username, message, hour, minute):
        self.schedule_type = "daily"
        self.schedule_hour = hour
        self.schedule_minute = minute
        schedule_time = f"{hour:02d}:{minute:02d}"
        schedule.every().day.at(schedule_time).do(self.run_scheduled_dm, username, message)
        print(f"✓ DM terjadwal setiap hari pukul {schedule_time}")
    
    def run_scheduled_dm(self, username, message):
        print(f"\n>>> Menjalankan DM terjadwal untuk @{username} <<<")
        self.send_dm(username, message)

def run_schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    os.system('clear')
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - CLI TERMUX")
    print("="*60)
    
    bot = TikTokAutoDM()
    
    if not os.path.exists('cookies_backup.json'):
        print("\n⚠️  BELUM ADA COOKIES!")
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
            bot.send_dm(username, pesan)
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