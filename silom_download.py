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

# บังคับเซฟไฟล์ไว้ในโฟลเดอร์เดียวกับโค้ดเพื่อให้ GitHub Actions ดึงไฟล์ไปบันทึกต่อได้ง่าย
DOWNLOAD_DIR = os.path.dirname(os.path.abspath(__file__))

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

# บังคับรันแบบ Headless (ซ่อนหน้าต่าง) และตั้งค่าสำหรับทำงานบน Linux Server ของ GitHub
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print("กำลังสั่งเปิด Chrome (Headless) บน GitHub Actions...")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

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
    time.sleep(4)
    
    try:
        driver.execute_script("""
            var modals = document.querySelectorAll('.v-modal, .el-dialog__wrapper, .modal-backdrop, [role="dialog"]');
            modals.forEach(function(el) { el.remove(); });
            document.body.style.overflow = 'auto';
            var chats = document.querySelectorAll('#crisp-chat-box, .crisp-client, [class^="cc-"]');
            chats.forEach(function(el) { el.remove(); });
        """)
    except Exception:
        pass

    print("กำลังสลับเมนูตรงไปยังหน้ารายงาน...")
    menu_inventory = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//*[contains(@class, 'sidebar') or contains(@class, 'menu')]//*[contains(text(), 'สินค้าคงคลัง')]"
    )))
    menu_inventory.click()
    time.sleep(1)
    
    submenu_sku = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//*[contains(@class, 'sidebar') or contains(@class, 'menu')]//*[contains(text(), 'สินค้าคงเหลือตาม SKU')]"
    )))
    submenu_sku.click()
    time.sleep(3)

    print("กำลังค้นหาปุ่ม 'ส่งออกไฟล์'...")
    export_button = wait.until(EC.presence_of_element_located((By.ID, "SKUInventoryExportButton")))
    
    print("กำลังส่งคำสั่งดาวน์โหลดไฟล์ Excel...")
    driver.execute_script("arguments[0].click();", export_button)
    
    # หน่วงเวลารอให้ดาวน์โหลดไฟล์เสร็จสมบูรณ์บนคลาวด์ก่อนปิดระบบ
    time.sleep(8)
    print("🎉 ดาวน์โหลดไฟล์ลงบนเซิร์ฟเวอร์เสร็จเรียบร้อยแล้ว!")

except Exception as e:
    print(f"เกิดข้อผิดพลาดในการทำงาน: {str(e)}")

finally:
    driver.quit()