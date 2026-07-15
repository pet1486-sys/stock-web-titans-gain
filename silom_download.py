import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================================
# CONFIGURATION: ข้อมูลบัญชีผู้ใช้
# ==========================================================
USERNAME = "pet1486@gmail.com"
PASSWORD = "htz32151"

DOWNLOAD_DIR = "/home/runner/Downloads"
SCREENSHOT_DIR = "/home/runner/work_screenshots" # โฟลเดอร์เก็บภาพหน้าจอ

for folder in [DOWNLOAD_DIR, SCREENSHOT_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": DOWNLOAD_DIR, 
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
chrome_options.add_argument("--window-size=1920,1080")

print("กำลังสั่งเปิด Chrome (Headless) บน GitHub Actions...")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    print("กำลังเปิดหน้าเว็บไซต์ Silom POS...")
    driver.get("https://dashboard.silompos.com/login")
    
    print("กำลังกรอกข้อมูลเข้าสู่ระบบ...")
    username_input = wait.until(EC.presence_of_element_located((
        By.XPATH, "//input[@type='text' or @type='email' or @autocomplete='username']"
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
    
    print("กำลังดักรอปุ่ม 'ส่งออกไฟล์' ปраกฏ...")
    export_button = wait.until(EC.presence_of_element_located((By.ID, "SKUInventoryExportButton")))
    time.sleep(5)
    
    # 📸 จุดถ่ายรูปที่ 1: ถ่ายรูปหน้าตารางรายงานสินค้า เพื่อดูว่าตารางและปุ่มขึ้นมาปกติไหม
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "1_before_click.png"))
    print("📸 บันทึกภาพหน้าจอก่อนกดปุ่มส่งออกไฟล์เรียบร้อย")

    print("กำลังใช้ JavaScript สั่งกดส่งออกไฟล์ Excel...")
    driver.execute_script("arguments[0].click();", export_button)
    
    print("⏱️ รอระบบบันทึกไฟล์ลงดิสก์บนเซิร์ฟเวอร์ 15 วินาที...")
    time.sleep(15)
    
    # 📸 จุดถ่ายรูปที่ 2: ถ่ายรูปหลังกดส่งออกไปแล้ว เผื่อมีแจ้งเตือนอะไรเด้งขึ้นมาแทรก
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "2_after_click.png"))
    print("📸 บันทึกภาพหน้าจอหลังกดปุ่มส่งออกไฟล์เรียบร้อย")
    
    files = os.listdir(DOWNLOAD_DIR)
    print(f"ไฟล์ที่พบในโฟลเดอร์ดาวน์โหลด: {files}")

except Exception as e:
    print(f"เกิดข้อผิดพลาดในการทำงาน: {str(e)}")
    # 📸 จุดถ่ายรูปกรณีพิเศษ: ถ้าเกิดเออเร่อกลางคัน ให้รีบแคปภาพหน้าจอ ณ วินาทีนั้นทันที
    try:
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "error_screenshot.png"))
        print("📸 บันทึกภาพหน้าจอขณะเกิดข้อผิดพลาดเรียบร้อย")
    except Exception:
        pass
    raise e

finally:
    driver.quit()
