#!/usr/bin/env python3
import os
import subprocess
import time
import signal
import sys
import threading
from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import schedule

class TikTokAutoDM:
    def __init__(self):
        self.scheduled_jobs = []
        self.schedule_type = None
        self.schedule_hour = None
        self.schedule_minute = None
        self.schedule_day = None
        
    def setup_xvfb(self):
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
        subprocess.Popen(
            [xvfb_path, f":{display_num}", "-screen", "0", "1280x720x16"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        time.sleep(2)
        os.environ['DISPLAY'] = f":{display_num}"
        
        result = subprocess.run(['pgrep', '-x', 'Xvfb'], capture_output=True)
        if result.returncode == 0:
            print(f"✓ Xvfb berjalan di display :{display_num}")
            return True
        else:
            print("✗ Gagal menjalankan Xvfb")
            return False
    
    def kill_xvfb(self):
        """Matikan Xvfb"""
        subprocess.run(['pkill', '-x', 'Xvfb'], capture_output=True)
        print("✓ Xvfb dimatikan")
    
    def send_dm(self, username, message, is_scheduled=False):
        """Kirim DM dengan screenshot setiap langkah"""
        
        print("\n" + "="*60)
        if is_scheduled:
            print("  TIKTOK AUTO DM - SCHEDULED")
        else:
            print("  TIKTOK AUTO DM - PLAYWRIGHT")
        print("="*60)
        print(f"Target : @{username}")
        print(f"Pesan  : {message}")
        print(f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Auto setup Xvfb
        if not self.setup_xvfb():
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
                
                # Load cookies
                print("> Memuat cookies...")
                if not os.path.exists('cookies_backup.json'):
                    print("✗ File cookies_backup.json tidak ditemukan!")
                    return False
                    
                with open('cookies_backup.json') as f:
                    cookies = json.load(f)
                    context.add_cookies(cookies)
                print(f"  Loaded {len(cookies)} cookies")
                
                # Buka TikTok
                print("\n> Membuka TikTok...")
                page.goto('https://www.tiktok.com', timeout=60000)
                page.wait_for_load_state('networkidle')
                if not is_scheduled:
                    page.screenshot(path="01_homepage.png")
                    print("  📸 Screenshot: 01_homepage.png")
                time.sleep(2)
                
                # Buka profile
                print(f"\n> Membuka profile @{username}...")
                page.goto(f'https://www.tiktok.com/@{username}', timeout=60000)
                page.wait_for_load_state('networkidle')
                if not is_scheduled:
                    page.screenshot(path="02_profile.png")
                    print("  📸 Screenshot: 02_profile.png")
                time.sleep(3)
                
                # Cari tombol Message
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
                    if not is_scheduled:
                        page.screenshot(path="03_after_click_msg.png")
                        print("  📸 Screenshot: 03_after_click_msg.png")
                else:
                    print("  ✗ Tombol Message tidak ditemukan!")
                    if not is_scheduled:
                        page.screenshot(path="error_no_message.png")
                    return False
                
                # Cari textarea
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
                    if not is_scheduled:
                        page.screenshot(path="04_before_type.png")
                        print("  📸 Screenshot: 04_before_type.png")
                    
                    # Kirim pesan
                    print(f"\n> Mengirim pesan...")
                    textarea.fill(message)
                    time.sleep(1)
                    if not is_scheduled:
                        page.screenshot(path="05_after_type.png")
                        print("  📸 Screenshot: 05_after_type.png")
                    
                    page.keyboard.press('Enter')
                    time.sleep(2)
                    
                    # Screenshot bukti
                    screenshot_name = f"06_sent_{username}_{int(time.time())}.png"
                    page.screenshot(path=screenshot_name)
                    print(f"  📸 Screenshot bukti: {screenshot_name}")
                    
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
                    if not is_scheduled:
                        page.screenshot(path="error_no_textarea.png")
                    return False
                    
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False
    
    def schedule_daily(self, username, message, hour, minute):
        """Schedule DM setiap hari"""
        self.schedule_type = "daily"
        self.schedule_hour = hour
        self.schedule_minute = minute
        schedule_time = f"{hour:02d}:{minute:02d}"
        
        schedule.every().day.at(schedule_time).do(
            self.send_dm_with_retry, username, message, True
        )
        
        self.scheduled_jobs.append(f"Daily at {schedule_time}")
        print(f"\n✓ DM terjadwal setiap hari pukul {schedule_time}")
        return True
    
    def schedule_weekly(self, username, message, day, hour, minute):
        """Schedule DM setiap minggu"""
        self.schedule_type = "weekly"
        self.schedule_hour = hour
        self.schedule_minute = minute
        self.schedule_day = day
        schedule_time = f"{hour:02d}:{minute:02d}"
        
        day_map = {
            0: schedule.every().monday,
            1: schedule.every().tuesday,
            2: schedule.every().wednesday,
            3: schedule.every().thursday,
            4: schedule.every().friday,
            5: schedule.every().saturday,
            6: schedule.every().sunday
        }
        
        day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        
        day_map[day].at(schedule_time).do(
            self.send_dm_with_retry, username, message, True
        )
        
        self.scheduled_jobs.append(f"Weekly on {day_names[day]} at {schedule_time}")
        print(f"\n✓ DM terjadwal setiap {day_names[day]} pukul {schedule_time}")
        return True
    
    def schedule_custom_date(self, username, message, year, month, day, hour, minute):
        """Schedule DM pada tanggal tertentu"""
        from datetime import datetime as dt
        import threading
        
        target_time = dt(year, month, day, hour, minute)
        current_time = dt.now()
        
        if target_time <= current_time:
            print("✗ Waktu yang dimasukkan sudah lewat!")
            return False
        
        delay_seconds = (target_time - current_time).total_seconds()
        
        print(f"\n✓ DM dijadwalkan pada: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Akan dijalankan dalam {int(delay_seconds // 3600)} jam {int((delay_seconds % 3600) // 60)} menit")
        
        timer = threading.Timer(delay_seconds, self.send_dm_with_retry, [username, message, True])
        timer.daemon = True
        timer.start()
        
        self.scheduled_jobs.append(f"Custom date: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    
    def send_dm_with_retry(self, username, message, is_scheduled=False, max_retry=3):
        """Kirim dengan retry logic"""
        
        for attempt in range(max_retry):
            print(f"\n📌 Percobaan ke-{attempt + 1} dari {max_retry}")
            
            success = self.send_dm(username, message, is_scheduled)
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
    
    def show_scheduled_jobs(self):
        """Tampilkan semua jadwal yang aktif"""
        if not self.scheduled_jobs:
            print("\n⚠️ Belum ada jadwal yang diatur")
        else:
            print("\n" + "="*60)
            print("  JADWAL AKTIF")
            print("="*60)
            for i, job in enumerate(self.scheduled_jobs, 1):
                print(f"{i}. {job}")
            print("="*60)
    
    def stop_all_schedules(self):
        """Stop semua schedule"""
        schedule.clear()
        self.scheduled_jobs = []
        self.schedule_type = None
        print("\n✓ Semua jadwal telah dihentikan")
    
    def run_schedule_loop(self):
        """Loop untuk menjalankan schedule"""
        print("\n⏰ Schedule loop berjalan...")
        print("   Tekan Ctrl+C untuk berhenti\n")
        
        while True:
            schedule.run_pending()
            time.sleep(1)

def main():
    os.system('clear')
    
    print("\n" + "="*60)
    print("  TIKTOK AUTO DM - COMPLETE EDITION")
    print("="*60)
    
    bot = TikTokAutoDM()
    
    # Cek cookies
    if not os.path.exists('cookies_backup.json'):
        print("\n⚠️ File cookies_backup.json tidak ditemukan!")
        print("\nCara membuat:")
        print("1. Install extension 'EditThisCookie' di Chrome PC")
        print("2. Login ke TikTok")
        print("3. Export cookies ke JSON")
        print("4. Simpan sebagai cookies_backup.json")
        return
    
    while True:
        print("\n" + "="*60)
        print("  MENU UTAMA")
        print("="*60)
        print("1. Kirim DM sekarang")
        print("2. Jadwalkan DM")
        print("3. Lihat jadwal aktif")
        print("4. Hentikan semua jadwal")
        print("5. Keluar")
        print("="*60)
        
        menu = input("\nPilih menu (1-5): ").strip()
        
        if menu == "1":
            # Kirim sekarang
            username = input("\n> Username target (tanpa @): ").strip()
            if not username:
                print("Username tidak boleh kosong!")
                continue
            
            pesan = input("> Pesan: ").strip()
            if not pesan:
                pesan = "Halo!"
            
            print("\n1. Kirim biasa")
            print("2. Kirim dengan retry (3x)")
            pilih = input("\nPilih (1/2): ")
            
            confirm = input(f"\nKirim ke @{username}? (y/n): ")
            if confirm.lower() == 'y':
                if pilih == "1":
                    bot.send_dm(username, pesan, is_scheduled=False)
                elif pilih == "2":
                    bot.send_dm_with_retry(username, pesan, is_scheduled=False)
                else:
                    print("Pilihan tidak valid!")
        
        elif menu == "2":
            # Jadwalkan DM
            print("\n" + "="*60)
            print("  JADWALKAN DM")
            print("="*60)
            print("1. Setiap hari (daily)")
            print("2. Setiap minggu (weekly)")
            print("3. Tanggal tertentu")
            print("="*60)
            
            jadwal_type = input("\nPilih jenis jadwal (1-3): ").strip()
            
            username = input("\n> Username target (tanpa @): ").strip()
            if not username:
                print("Username tidak boleh kosong!")
                continue
            
            pesan = input("> Pesan: ").strip()
            if not pesan:
                pesan = "Halo!"
            
            if jadwal_type == "1":
                # Daily schedule
                print("\n" + "-"*40)
                while True:
                    try:
                        jam = int(input("Jam (0-23): "))
                        if 0 <= jam <= 23:
                            break
                        print("   Jam harus 0-23")
                    except:
                        print("   Masukkan angka!")
                
                while True:
                    try:
                        menit = int(input("Menit (0-59): "))
                        if 0 <= menit <= 59:
                            break
                        print("   Menit harus 0-59")
                    except:
                        print("   Masukkan angka!")
                
                print("\n" + "="*60)
                print("  KONFIRMASI JADWAL")
                print("="*60)
                print(f"Target : @{username}")
                print(f"Pesan  : {pesan}")
                print(f"Jadwal : Setiap hari pukul {jam:02d}:{menit:02d}")
                print("="*60)
                
                confirm = input("\nAktifkan jadwal? (y/n): ")
                if confirm.lower() == 'y':
                    bot.schedule_daily(username, pesan, jam, menit)
                    bot.run_schedule_loop()
            
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
                        hari = int(input("\nPilih (1-7): "))
                        if 1 <= hari <= 7:
                            break
                        print("   Pilihan 1-7")
                    except:
                        print("   Masukkan angka!")
                
                while True:
                    try:
                        jam = int(input("Jam (0-23): "))
                        if 0 <= jam <= 23:
                            break
                        print("   Jam harus 0-23")
                    except:
                        print("   Masukkan angka!")
                
                while True:
                    try:
                        menit = int(input("Menit (0-59): "))
                        if 0 <= menit <= 59:
                            break
                        print("   Menit harus 0-59")
                    except:
                        print("   Masukkan angka!")
                
                day_names = {1:"Senin", 2:"Selasa", 3:"Rabu", 4:"Kamis", 5:"Jumat", 6:"Sabtu", 7:"Minggu"}
                day_map = {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6}
                
                print("\n" + "="*60)
                print("  KONFIRMASI JADWAL")
                print("="*60)
                print(f"Target : @{username}")
                print(f"Pesan  : {pesan}")
                print(f"Jadwal : Setiap {day_names[hari]} pukul {jam:02d}:{menit:02d}")
                print("="*60)
                
                confirm = input("\nAktifkan jadwal? (y/n): ")
                if confirm.lower() == 'y':
                    bot.schedule_weekly(username, pesan, day_map[hari], jam, menit)
                    bot.run_schedule_loop()
            
            elif jadwal_type == "3":
                # Custom date
                print("\nMasukkan tanggal dan waktu:")
                
                while True:
                    try:
                        tahun = int(input("Tahun (2024-2030): "))
                        if 2024 <= tahun <= 2030:
                            break
                        print("   Tahun 2024-2030")
                    except:
                        print("   Masukkan angka!")
                
                while True:
                    try:
                        bulan = int(input("Bulan (1-12): "))
                        if 1 <= bulan <= 12:
                            break
                        print("   Bulan 1-12")
                    except:
                        print("   Masukkan angka!")
                
                while True:
                    try:
                        hari = int(input("Hari (1-31): "))
                        if 1 <= hari <= 31:
                            break
                        print("   Hari 1-31")
                    except:
                        print("   Masukkan angka!")
                
                while True:
                    try:
                        jam = int(input("Jam (0-23): "))
                        if 0 <= jam <= 23:
                            break
                        print("   Jam 0-23")
                    except:
                        print("   Masukkan angka!")
                
                while True:
                    try:
                        menit = int(input("Menit (0-59): "))
                        if 0 <= menit <= 59:
                            break
                        print("   Menit 0-59")
                    except:
                        print("   Masukkan angka!")
                
                print("\n" + "="*60)
                print("  KONFIRMASI JADWAL")
                print("="*60)
                print(f"Target : @{username}")
                print(f"Pesan  : {pesan}")
                print(f"Jadwal : {tahun}-{bulan:02d}-{hari:02d} {jam:02d}:{menit:02d}")
                print("="*60)
                
                confirm = input("\nAktifkan jadwal? (y/n): ")
                if confirm.lower() == 'y':
                    bot.schedule_custom_date(username, pesan, tahun, bulan, hari, jam, menit)
            
            else:
                print("Pilihan tidak valid!")
        
        elif menu == "3":
            # Lihat jadwal
            bot.show_scheduled_jobs()
        
        elif menu == "4":
            # Hentikan semua jadwal
            confirm = input("\nHentikan semua jadwal? (y/n): ")
            if confirm.lower() == 'y':
                bot.stop_all_schedules()
        
        elif menu == "5":
            # Keluar
            print("\n> Terima kasih! Sampai jumpa!")
            bot.kill_xvfb()
            break
        
        else:
            print("Pilihan tidak valid!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n> Dihentikan user")
    except Exception as e:
        print(f"\n> Error: {e}")