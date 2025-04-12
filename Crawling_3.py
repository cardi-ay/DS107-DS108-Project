import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# ===== 1. Cấu hình Chrome =====
options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

# ===== 2. Truy cập trang chứa hỏi đáp =====
url = "https://dichvucong.moh.gov.vn/web/guest/hoi-dap?p_p_id=hoidap_WAR_oephoidapportlet&_hoidap_WAR_oephoidapportlet_delta=9999"
driver.get(url)
time.sleep(3)

data = []
main_tab = driver.current_window_handle

# ===== 3. Lấy tất cả khối hỏi đáp =====
qa_blocks = driver.find_elements(By.CSS_SELECTOR, "div.panel.panel-default")
print(f"🔍 Tìm thấy {len(qa_blocks)} khối hỏi đáp.")

for block in qa_blocks:
    try:
        # 🔹 Lấy số câu hỏi con từ badge
        try:
            badge_el = block.find_element(By.CSS_SELECTOR, "span.badge.badge-primary.badge-pill")
            badge_count = badge_el.text.strip()
        except:
            badge_count = "0"

        # 🔹 Lấy link để mở chi tiết
        link_el = block.find_element(By.CSS_SELECTOR, "a[href]")
        link = link_el.get_attribute("href")

        # ===== Mở chi tiết trong tab mới =====
        driver.execute_script("window.open(arguments[0]);", link)
        time.sleep(1)

        tabs = driver.window_handles
        driver.switch_to.window(tabs[-1])  # chuyển sang tab mới

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[onclick*="showtraloi"]'))
            )
            show_btn = driver.find_element(By.CSS_SELECTOR, '[onclick*="showtraloi"]')
            driver.execute_script("arguments[0].click();", show_btn)
            time.sleep(1)
        except:
            print("⚠️ Không tìm thấy nút showtraloi.")
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        question = soup.find("div", class_="question-content")
        answer = soup.find("div", class_="col-md-12")

        question_text = question.get_text(strip=True) if question else "Không tìm thấy câu hỏi"
        answer_text = answer.get_text(strip=True) if answer else "Không tìm thấy câu trả lời"

        data.append({
            "question": question_text,
            "answer": answer_text,
            "link": driver.current_url,
            "sub_question_count": badge_count
        })

        print(f"✅ {question_text[:50]}... | Trao đổi: {badge_count}")

        driver.close()
        driver.switch_to.window(main_tab)

    except Exception as e:
        print(f"❌ Lỗi xử lý 1 mục: {e}")
        try:
            driver.close()
            driver.switch_to.window(main_tab)
        except:
            pass
        continue

# ===== 4. Ghi file kết quả =====
df = pd.DataFrame(data)
df.to_csv("qa_dvc_with_badge.csv", index=False, encoding="utf-8-sig")
print(f"\n🎉 Đã lưu {len(df)} câu hỏi - trả lời vào qa_dvc_with_badge.csv")

driver.quit()
