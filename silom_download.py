import os
import sys
import time
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# สั่งให้ Python พิมพ์ข้อความเรียงตามบรรทัดจริงบน GitHub Actions ป้องกัน Logs สลับกัน
sys.stdout.reconfigure(line_buffering=True)

# ==========================================================
# CONFIGURATION: ข้อมูลบัญชีผู้ใช้ และตำแหน่งจัดเก็บ
# ==========================================================
USERNAME = "pet1486@gmail.com"
PASSWORD = "htz32151"

# ปรับตำแหน่งโฟลเดอร์ให้บันทึกลงในคลังสต็อกของเว็บโดยตรงเพื่อความสะดวก
DOWNLOAD_DIR = "stock_data" 
SCREENSHOT_DIR = "/home/runner/work_screenshots" 

for folder in [DOWNLOAD_DIR, SCREENSHOT_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# ไฟล์ปลายทางหลักสำหรับหน้าเว็บ
target_excel_path = os.path.join(DOWNLOAD_DIR, "SKU.xlsx")

chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": os.path.abspath(DOWNLOAD_DIR), 
    "download.prompt_for_download": False,        
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.password_manager_leak_detection": False,
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
}
chrome_options.add_experimental_option("prefs", prefs)

chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1440,900")

print("กำลังสั่งเปิด Chrome (Headless) บน GitHub Actions...")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

# ==========================================================
# ส่วนที่ 1: ดาวน์โหลดไฟล์ด้วย Selenium
# ==========================================================
try:
    print("กำลังเปิดหน้าเว็บไซต์ Silom POS...")
    driver.get("https://dashboard.silompos.com/login")
    
    print("กำลังกรอกข้อมูลเข้าสู่ระบบ...")
    username_input = wait.until(EC.presence_of_element_located((
        By.開設, "//input[@type='text' or @type='email' or @autocomplete='username']"
    )))
    username_input.clear()
    username_input.send_keys(USERNAME)
    
    password_input = driver.find_element(By.XPATH, "//input[@type='password']")
    password_input.clear()
    password_input.send_keys(PASSWORD)
    
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign In')]")))
    login_button.click()
    
    print("กำลังรอโหลดหน้า Dashboard...")
    time.sleep(8)
    
    try:
        driver.execute_script("""
            var modals = document.querySelectorAll('.v-modal, .el-dialog__wrapper, .modal-backdrop, [role="dialog"]');
            modals.forEach(function(el) { el.remove(); });
            document.body.style.overflow = 'auto';
            var chats = document.querySelectorAll('#crisp-chat-box, .crisp-client, [class^="cc-"]');
            chats.forEach(function(el) { el.remove(); });
        """)
        print("ล้างสิ่งกีดขวางหน้าจอเรียบร้อย")
    except Exception:
        pass

    print("กำลังคลิกหัวข้อหลัก 'สินค้าคงคลัง'...")
    menu_inventory = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//*[contains(@class, 'sidebar') or contains(@class, 'menu')]//*[contains(text(), 'สินค้าคงคลัง')]"
    )))
    menu_inventory.click()
    time.sleep(2)
    
    print("กำลังคลิกเมนูย่อย 'สินค้าคงเหลือตาม SKU'...")
    submenu_sku = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//*[contains(@class, 'sidebar') or contains(@class, 'menu')]//*[contains(text(), 'สินค้าคงเหลือตาม SKU')]"
    )))
    submenu_sku.click()
    
    print("กำลังดักรอปุ่ม 'ส่งออกไฟล์' ปรากฏ...")
    export_button = wait.until(EC.presence_of_element_located((By.ID, "SKUInventoryExportButton")))
    time.sleep(5)
    
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "1_before_click.png"))
    print("📸 บันทึกภาพหน้าจอก่อนกดปุ่มส่งออกไฟล์เรียบร้อย")

    print("กำลังใช้ JavaScript สั่งกดส่งออกไฟล์ Excel...")
    driver.execute_script("arguments[0].click();", export_button)
    
    print("⏱️ รอระบบบันทึกไฟล์ลงดิสก์บนเซิร์ฟเวอร์ 15 วินาที...")
    time.sleep(15)
    
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "2_after_click.png"))
    print("📸 บันทึกภาพหน้าจอหลังกดปุ่มส่งออกไฟล์เรียบร้อย")
    
    files = os.listdir(DOWNLOAD_DIR)
    print(f"ไฟล์ที่พบในโฟลเดอร์ดาวน์โหลดขณะนี้: {files}")

    # ตรวจหาไฟล์ที่เพิ่งดาวน์โหลดลงมาแล้วจับเปลี่ยนชื่อเป็น SKU.xlsx
    excel_files = [f for f in files if f.endswith('.xlsx') and f != 'SKU.xlsx']
    if excel_files:
        latest_downloaded = max([os.path.join(DOWNLOAD_DIR, f) for f in excel_files], key=os.path.getctime)
        if os.path.exists(target_excel_path):
            os.remove(target_excel_path)
        os.rename(latest_downloaded, target_excel_path)
        print(f"✅ ซิงค์และเปลี่ยนชื่อไฟล์สำเร็จที่: {target_excel_path}")
    elif not os.path.exists(target_excel_path):
        raise FileNotFoundError("บอทหาไฟล์ Excel สต็อกที่ดาวน์โหลดใหม่ไม่เจอในระบบ")

except Exception as e:
    print(f"เกิดข้อผิดพลาดในการทำงาน: {str(e)}")
    try:
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "error_screenshot.png"))
        print("📸 บันทึกภาพหน้าจอขณะเกิดข้อผิดพลาดเรียบร้อย")
    except Exception:
        pass
    raise e
finally:
    driver.quit()


# ==========================================================
# ส่วนที่ 2: ตรวจสอบความต่างสต็อก On Hand และบันทึกไฟล์ Log แยกรายเดือน
# ==========================================================
print("\n--- เริ่มกระบวนการประมวลผลสต็อกและแยกสร้างไฟล์คลังรายงานประวัติรายเดือน ---")
try:
    # คำนวณวันเวลาของไทย
    th_time = datetime.utcnow() + timedelta(hours=7)
    date_str = th_time.strftime('%Y-%m-%d')
    time_str = th_time.strftime('%H:%M')
    full_timestamp = f"{date_str} {time_str}"
    
    # ตั้งชื่อไฟล์แบบแยกรายเดือน เช่น stock_data/logs_2026_07.json
    month_suffix = th_time.strftime('%Y_%m')
    monthly_log_path = os.path.join(DOWNLOAD_DIR, f"logs_{month_suffix}.json")
    balance_history_path = os.path.join(DOWNLOAD_DIR, "last_balances.json")
    
    # เปิดอ่านไส้ในไฟล์ Excel ด้วยคัดกรองแบบเดียวกับหน้าเว็บ
    df = pd.read_excel(target_excel_path, header=7)
    target_categories = ["อุปกรณ์ปะยาง", "อุปกรณ์ปะยาง MR"]
    df_filtered = df[df.iloc[:, 6].astype(str).str.trim().isin(target_categories)]
    
    # ดึงข้อมูลยอดคงเหลือสต็อกของรอบที่แล้วมาเปรียบเทียบ
    previous_stock = {}
    if os.path.exists(balance_history_path):
        with open(balance_history_path, 'r', encoding='utf-8') as f:
            previous_stock = json.load(f)
            
    # โหลดไฟล์ Log เดิมของเดือนนี้ขึ้นมาตั้งต้น (ถ้ามีอยู่แล้วในคลัง)
    fill_logs = []
    sales_logs = []
    if os.path.exists(monthly_log_path):
        with open(monthly_log_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            fill_logs = existing_data.get("fill_logs", [])
            sales_logs = existing_data.get("sales_logs", [])

    current_stock = {}
    has_changes = False
    
    for _, row in df_filtered.iterrows():
        plu = str(row.iloc[0]).strip()
        name = str(row.iloc[1]).strip()
        
        # 🌟 จุดแก้ไข: ล้างอักขระพิเศษสำหรับใช้เรียกรูปภาพ (แปลง < > เป็น ( ) และ ช่องว่าง เป็น _)
        image_name = name.replace("<", "(").replace(">", ")").replace(" ", "_") + ".png"
        
        try:
            qty = int(row.iloc[7])
        except:
            qty = 0
            
        current_stock[plu] = qty
        
        # คำนวณหากลุ่มผลต่างความเปลี่ยนแปลง
        if plu in previous_stock:
            diff = qty - previous_stock[plu]
            if diff > 0:
                fill_logs.insert(0, [full_timestamp, plu, name, f"+{diff} ชิ้น"])
                has_changes = True
            elif diff < 0:
                sales_logs.insert(0, [full_timestamp, plu, name, f"{abs(diff)} ชิ้น"])
                has_changes = True

    # เซฟยอด On Hand ล่าสุดเก็บไว้เทียบกับวันถัดไป
    with open(balance_history_path, 'w', encoding='utf-8') as f:
        json.dump(current_stock, f, ensure_ascii=False, indent=2)
        
    # หากมีการขยับของเลข On Hand ให้ทำการเซฟและดันเข้าไฟล์ Log ประจำเดือนนั้นๆ
    if has_changes or not os.path.exists(monthly_log_path):
        log_data = {"fill_logs": fill_logs, "sales_logs": sales_logs}
        with open(monthly_log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        print(f"📝 อัปเดตไฟล์บันทึกประวัติสำเร็จที่: {monthly_log_path}")
    else:
        print("✅ ยอดคงเหลือเท่าเดิมไม่มีการขยับตัว ไม่ต้องอัปเดตไฟล์ Log เพิ่มเติม")

except Exception as log_err:
    print(f"⚠️ เกิดปัญหาในระบบการคำนวณเขียนไฟล์ประวัติ: {str(log_err)}")