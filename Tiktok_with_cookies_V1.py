import requests
import json
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TikTokAutoDM:
    def __init__(self):
        self.driver = None
        self.cookies = None
        
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
            print(f"\n❌ Format JSON error: {e}")
            return False
    
    def send_dm(self, username, message):
        """Kirim DM ke username tertentu"""
        
        print("\n" + "="*60)
        print("  MENGIRIM DM VIA BROWSER")
        print("="*60)
        print(f"Target : @{username}")
        print(f"Pesan  : {message}")
        print("="*60)
        
        print("\n> Membuka browser...")
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Buka TikTok
        print("> Membuka TikTok...")
        self.driver.get("https://www.tiktok.com")
        time.sleep(3)
        
        # Apply cookies ke browser
        print("> Memuat cookies...")
        for cookie in self.cookies:
            try:
                clean_cookie = {
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    'domain': cookie.get('domain', '.tiktok.com'),
                    'path': cookie.get('path', '/')
                }
                if cookie.get('secure'):
                    clean_cookie['secure'] = True
                
                self.driver.add_cookie(clean_cookie)
            except:
                pass
        
        print("> Cookies loaded")
        self.driver.refresh()
        time.sleep(5)
        
        # Buka profile target
        print(f"\n> Membuka profile @{username}...")
        self.driver.get(f"https://www.tiktok.com/@{username}")
        time.sleep(5)
        
        self.driver.save_screenshot("01_profile_page.png")
        print("📸 Screenshot: 01_profile_page.png")
        
        try:
            # Cari tombol Message
            print("> Mencari tombol Message...")
            msg_selectors = [
                "//div[@data-testid='tux-web-text' and text()='Message']",
                "//div[contains(@class, 'tux-web-canary') and text()='Message']",
                "//button[.//div[text()='Message']]",
            ]
            
            msg_btn = None
            for selector in msg_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            if elem.tag_name == 'div':
                                parent_btn = elem.find_element(By.XPATH, './ancestor::button')
                                if parent_btn:
                                    msg_btn = parent_btn
                                    break
                            else:
                                msg_btn = elem
                                break
                    if msg_btn:
                        break
                except:
                    continue
            
            if msg_btn:
                self.driver.execute_script("arguments[0].click();", msg_btn)
                print("> Tombol Message diklik!")
                time.sleep(5)
            else:
                print("> Tombol Message tidak ditemukan!")
                print("   Kemungkinan: Akun target tidak bisa di-DM")
                self.driver.save_screenshot("02_no_message_button.png")
                return False
            
            # Cari textarea dan kirim pesan
            print("> Mencari textarea...")
            textarea_selectors = [
                "//textarea[@placeholder='Send a message...']",
                "//textarea[@aria-label='Message']",
                "//div[@contenteditable='true']",
                "//textarea"
            ]
            
            textarea = None
            for selector in textarea_selectors:
                try:
                    textarea = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if textarea:
                        break
                except:
                    continue
            
            if textarea:
                textarea.click()
                time.sleep(1)
                
                # Kirim pesan per karakter (biar natural)
                for char in message:
                    textarea.send_keys(char)
                    time.sleep(0.03)
                
                time.sleep(1)
                textarea.send_keys(Keys.RETURN)
                
                print(f"\n~~~ PESAN BERHASIL TERKIRIM! ~~~")
                print(f"   Target: @{username}")
                print(f"   Pesan: {message}")
                
                time.sleep(2)
                
                # Screenshot bukti
                screenshot = f"dm_sent_{username}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot)
                print(f"📸 Screenshot bukti: {screenshot}")
                
                return True
            else:
                print("❌ Textarea tidak ditemukan!")
                self.driver.save_screenshot("03_no_textarea.png")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.driver.save_screenshot("04_error.png")
            return False
        
        finally:
            if self.driver:
                print("\n⏳ Browser akan ditutup dalam 5 detik...")
                time.sleep(5)
                self.driver.quit()

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - BY WXYYDESU")
    print("="*60)
    
    bot = TikTokAutoDM()
    
    # Cek apakah ada file cookies
    if not os.path.exists('cookies_backup.json'):
        print("\n⚠️  BELUM ADA COOKIES!")
        print("   Harus login dulu (hanya sekali)\n")
        
        if bot.get_cookies_from_input():
            print("\n> Login berhasil! Silakan jalankan ulang script.")
        else:
            print("\n> Gagal login!")
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
        pesan = "Halo!"  # default message
    
    # Konfirmasi
    print("\n" + "="*60)
    print("  KONFIRMASI")
    print("="*60)
    print(f"Target : @{username}")
    print(f"Pesan  : {pesan}")
    print("="*60)
    
    konfirmasi = input("\nKirim DM? (y/n): ").strip().lower()
    
    if konfirmasi == 'y':
        # Kirim DM
        bot.send_dm(username, pesan)
    else:
        print("❌ Dibatalkan")

if __name__ == "__main__":
    main()