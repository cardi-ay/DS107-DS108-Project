import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# ===== 1. Cấu hình thư mục tải & Chrome =====
download_folder = os.path.abspath("downloads")
os.makedirs(download_folder, exist_ok=True)

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_folder,
    "plugins.always_open_pdf_externally": True,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=chrome_options)

# ===== 2. Truy cập trang web =====
url = "https://emohbackup.moh.gov.vn/publish/home?isLaw=true"
driver.get(url)
time.sleep(4)

file_data = []
current_page = 1
target_end_page = 5  # bạn có thể điều chỉnh

# ===== 3. Duyệt từng trang và click icon PDF =====
while current_page <= target_end_page:
    print(f"\n📄 Đang xử lý trang {current_page}...")

    try:
        table = driver.find_element(By.ID, "document-list")

        # ⚠️ Sửa lại selector theo class chính xác của biểu tượng
        icons = table.find_elements(By.CSS_SELECTOR, "i.fa.fa-file-word-o")
        print(f"📎 Tìm thấy {len(icons)} biểu tượng PDF")

        for idx, icon in enumerate(icons):
            try:
                driver.execute_script("arguments[0].click();", icon)  # Click qua JS cho chắc
                print(f"⬇ Đang tải file {idx+1} trên trang {current_page}...")
                time.sleep(5)  # Chờ file tải xong
            except Exception as e:
                print(f"❌ Lỗi khi click file {idx+1}: {e}")
                continue

            file_data.append({
                "Trang": current_page,
                "STT": idx + 1
            })

    except NoSuchElementException:
        print("❌ Không tìm thấy bảng dữ liệu.")
        break

    # ===== 4. Chuyển sang trang tiếp theo =====
    try:
        pagination_links = driver.find_elements(By.TAG_NAME, "a")
        moved = False

        for btn in pagination_links:
            if btn.text.strip() == str(current_page + 1):
                print(f"➡️ Chuyển sang trang {current_page + 1}")
                btn.click()
                current_page += 1
                time.sleep(3)
                moved = True
                break

        if not moved:
            print("✅ Đã duyệt hết các trang.")
            break

    except Exception as e:
        print(f"❌ Lỗi khi chuyển trang: {e}")
        break

# ===== 5. Ghi dữ liệu file đã tải =====
df = pd.DataFrame(file_data)
df.to_csv("file_links.csv", index=False, encoding='utf-8-sig')

driver.quit()
print("\n🎉 HOÀN TẤT! Đã click tải toàn bộ PDF qua biểu tượng fa-file-pdf-o.")
