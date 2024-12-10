import os

def delete_images_with_suffix(folder_path, suffix=").jpg"):
    """
    刪除資料夾內名稱後墜為指定後綴的檔案。

    :param folder_path: 資料夾路徑
    :param suffix: 要刪除的後綴，預設為 ").jpg"
    """
    if not os.path.isdir(folder_path):
        print(f"資料夾 {folder_path} 不存在")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(suffix):
            file_path = os.path.join(folder_path, filename)
            try:
                os.remove(file_path)
                print(f"已刪除: {file_path}")
            except Exception as e:
                print(f"無法刪除 {file_path}：{e}")

# 使用範例
folder_path = "C:\\workspace\\flickr_downloader\\images\\wheelchair"  # 將此替換為你的資料夾路徑
delete_images_with_suffix(folder_path)
