"""
健保署醫學中心爬蟲 - 配置檔案
"""
from pathlib import Path
from datetime import datetime

# 專案根目錄
BASE_DIR = Path(__file__).parent

# 資料輸出目錄
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 日誌目錄
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 目標網址
TARGET_URL = "https://info.nhi.gov.tw/INAE4000/INAE4001S01"

# 輸出檔案名稱格式
def get_output_filename(extension="csv"):
    """
    生成帶時間戳的輸出檔案名稱
    
    Args:
        extension: 檔案副檔名 (csv 或 json)
    
    Returns:
        完整的檔案路徑
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"medical_centers_{timestamp}.{extension}"
    return DATA_DIR / filename

# 日誌檔案路徑
LOG_FILE = LOG_DIR / "scraper.log"

# Selenium 配置
SELENIUM_CONFIG = {
    "headless": True,           # 無頭模式（不顯示瀏覽器視窗）
    "wait_timeout": 10,         # 元素等待超時時間（秒）
    "page_load_timeout": 30,    # 頁面載入超時時間（秒）
}

# 爬蟲配置
SCRAPER_CONFIG = {
    "institution_level": "醫學中心",  # 查詢的院所層級
    "records_per_page": 50,           # 每頁顯示筆數（10, 20, 或 50）
    "retry_times": 3,                 # 失敗重試次數
    "retry_delay": 2,                 # 重試間隔（秒）
}

# 歷史資料累積檔案
HISTORY_FILE = DATA_DIR / "medical_centers_history.json"

# Email 通知設定
EMAIL_CONFIG = {
    "enabled": True,                  # 是否啟用 Email 通知
    "smtp_server": "smtp.gmail.com",  # SMTP 伺服器
    "smtp_port": 587,                 # SMTP 連接埠
    "sender_email": "kevintsaiudn@gmail.com",    # 寄件者 Email
    "sender_password": "lwtu oddb islc zbxw",    # 寄件者應用程式密碼
    "receiver_emails": ["kevintsaiudn@gmail.com"], # 收件者列表
    "subject_prefix": "[健保署重度級急救責任醫院急診即時訊息]",      # 郵件主旨前綴
}
