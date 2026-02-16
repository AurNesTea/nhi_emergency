
# 專案設定檔 (Configuration)

import os
from pathlib import Path
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# 專案根目錄
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# 確保目錄存在
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# 檔案路徑設定
LOG_FILE = LOG_DIR / "scraper.log"
HISTORY_FILE = DATA_DIR / "medical_centers_history.json"
WEB_DATA_FILE = BASE_DIR / "data.js"

# 爬蟲設定
TARGET_URL = 'https://info.nhi.gov.tw/INAE4000/INAE4001S01'

SCRAPER_CONFIG = {
    'retry_times': 3,
    'retry_delay': 2,
    'records_per_page': 50  # 一次顯示50筆，確保抓到所有資料
}

SELENIUM_CONFIG = {
    'headless': True,  # 預設為 True (無頭模式)
    'wait_timeout': 10,
    'page_load_timeout': 30
}

# 資料庫設定 (PostgreSQL)
DB_CONFIG = {
    'url': os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/nhi_db')
}

# Email 設定 (支援 Gmail / Outlook / SMTP)
EMAIL_CONFIG = {
    "enabled": False,  # 預設關閉，需手動開啟
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": os.getenv("EMAIL_SENDER", ""),
    "sender_password": os.getenv("EMAIL_PASSWORD", ""),  # 應用程式密碼
    "receiver_emails": os.getenv("EMAIL_RECEIVERS", "").split(","),
    "subject_prefix": "[健保署爬蟲通知]",
}

def get_output_filename(extension='csv'):
    """產生帶有時間戳記的輸出檔名 (但此邏輯已棄用，僅作相容保留)"""
    timestamp = os.getenv('SCRAPER_TIMESTAMP')
    if not timestamp:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    return DATA_DIR / f"medical_centers_{timestamp}.{extension}"
