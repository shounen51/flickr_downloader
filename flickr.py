from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import os
from utils import convert_to_timestamp, wait_for_download
import time
from tqdm import tqdm

def scrape_flickr_images(search_text, download_dir, t1=None, t2=None, start_page=1):
    """在 Flickr 上搜索並下載圖片"""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # 初始化 WebDriver
    service = Service("path_to_chromedriver")  # 替換為 ChromeDriver 的實際路徑
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,  # 設定下載路徑
        "download.prompt_for_download": False,          # 禁止每次下載時彈出對話框
        "download.directory_upgrade": True,            # 自動更新到新目錄
        "safebrowsing.enabled": True                   # 啟用安全下載
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    actions = ActionChains(driver)
    min_taken_date = f"&min_taken_date={convert_to_timestamp(t1)}" if t1 is not None else ""
    max_taken_date = f"&max_taken_date={convert_to_timestamp(t2)}" if t2 is not None else ""
    downloaded_jpg = 0
    try:
        for page in range(start_page, 100):
            # 打開搜索頁面
            search_url = f"https://www.flickr.com/search/?text={search_text}&view_all=1&content_types=0&dimension_search_mode=min&height=640&width=640"\
                            + min_taken_date + max_taken_date + f"&page={page}"
            print(f"Connecting: {search_url}")
            driver.get(search_url)
            time.sleep(1)  # 等待新分頁加載
            # 等待初始內容加載
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/main/div/div[1]"))
            )
            temp_conatiner = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div/div[1]")
            child_divs = temp_conatiner.find_elements(By.XPATH, "./div")
            # 獲取圖片鏈接
            container = driver.find_element(By.XPATH, f"/html/body/div[2]/div/main/div/div[1]/div[{len(child_divs)}]/div/div[2]")
            image_elements = container.find_elements(By.XPATH, "./div/div/div/div/a")
            for image_element in tqdm(image_elements[-min(50, len(image_elements)):]):
                try:
                    href = image_element.get_attribute("href")
                except:
                    continue
                
                driver.execute_script(f"window.open('{href}');")  # 開啟新分頁
                time.sleep(2)  # 等待新分頁加載

                # 切換到新分頁
                driver.switch_to.window(driver.window_handles[-1])
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div/div[5]/div[3]/a"))
                    )
                    btn = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div/div[5]/div[3]/a")
                    actions.move_to_element(btn).click().perform()
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/ul"))
                    )
                except:
                    driver.close()  # 關閉當前新分頁
                    driver.switch_to.window(driver.window_handles[0])  # 切換回主分頁
                    continue
                size_list = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/ul")
                li_elements = size_list.find_elements(By.XPATH, "li")
                # 獲取倒數第二個 <li>
                if len(li_elements) >= 2:
                    second_last_li = li_elements[-2]
                    
                    # 滑鼠點擊該元素
                    actions.move_to_element(second_last_li).click().perform()
                    downloaded_jpg += 1
                    # print("已點擊倒數第二個 <li> 元素")
                else:
                    print("列表元素不足 2")
                # 關閉新分頁，切換回主分頁
                driver.close()  # 關閉當前新分頁
                driver.switch_to.window(driver.window_handles[0])  # 切換回主分頁
            print(f"Close page {page}. Downloaded {downloaded_jpg} jpg.")

    finally:
        driver.quit()

if __name__ == "__main__":
    search_query = input("Enter search text: ")
    output_folder = f"C:\\workspace\\flickr_download\\images\\{search_query}"
    scrape_flickr_images(search_query, output_folder, "2022/1/1", "2022/12/31", 1)
    