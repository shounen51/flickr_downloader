import requests
import time
from datetime import datetime

def convert_to_timestamp(date_str):
    """將 YYYY/mm/DD 格式的日期轉換為 UNIX 時間戳"""
    try:
        # 使用 datetime.strptime 解析日期字串
        dt = datetime.strptime(date_str, "%Y/%m/%d")
        # 將 datetime 轉換為 UNIX 時間戳
        timestamp = int(dt.timestamp())
        return timestamp
    except ValueError:
        print("日期格式錯誤，請使用 YYYY/mm/DD 格式")
        return None
    
def download_image(url, save_path):
    """下載圖片到本地"""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return True
    else:
        print(f"Failed to download image: {url}")
        return False
        
# 等待檔案下載完成
def wait_for_download(folder, timeout=30):
    start_time = time.time()
    while True:
        if any([file.endswith(".crdownload") for file in os.listdir(folder)]):
            time.sleep(1)  # 等待下載完成
        else:
            break
        if time.time() - start_time > timeout:
            raise Exception("下載超時")
        
def scroll_to_load_more(driver, scroll_pause_time=2, max_scrolls=20):
    """滾動頁面以加載更多內容"""
    last_height = driver.execute_script("return document.body.scrollHeight")  # 初始頁面高度
    scrolls = 0

    while scrolls < max_scrolls:  # 限制最大滾動次數，避免陷入無限循環
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 滾動到頁面底部
        time.sleep(scroll_pause_time)  # 等待內容加載

        # 檢查頁面是否還有新的內容加載
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # 如果高度未變化，可能已加載完所有內容
            break

        last_height = new_height
        scrolls += 1

    print(f"Completed scrolling after {scrolls} scrolls.")
    