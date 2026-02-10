# 健保署醫學中心爬蟲 (NHI Medical Center Scraper)

> **專案狀態**: Production Ready (v2.1)  
> **最新更新**: 2026-02-10 (Email Notification Verified)  
> **交付日期**: 2026-02-13

## 專案概述

本專案旨在自動化抓取健保署網站上全台 28 家醫學中心的即時等待人數資料，並支援自動化排程與通知功能。程式經過優化，可一次性抓取全國資料，無需遍歷縣市，執行速度極快（約 10-15 秒）。

**主要功能：**
*   **高效爬蟲**: 使用 Selenium + Headless Chrome，單次執行僅需約 13 秒。
*   **完整數據**: 抓取住院、看診、推床、加護病房等待人數及滿床通報狀態。
*   **自動化重試**: 內建 `@retry_on_failure` 機制，遇到網絡波動自動重試。
*   **資料驗證**: 自動檢查抓取筆數（預期 28 筆），確保資料完整性。
*   **歷史累積**: 每次執行自動追加新資料至 `medical_centers_history.json`。
*   **Email 通知**: 支援 SMTP 發信及附件傳送，可設定多位收件人。
*   **Windows 排程**: 提供批次檔與部署指南，輕鬆設定每日自動執行。

**資料來源**: [健保署特約醫療院所資訊查詢](https://info.nhi.gov.tw/INAE4000/INAE4001S01)

---

## 快速開始

### 1. 環境需求
*   Python 3.10+
*   Google Chrome 瀏覽器

### 2. 安裝步驟

```bash
# Clone 專案
git clone [repository_url]
cd 健保署醫學中心爬蟲

# 建立虛擬環境 (建議)
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

# 安裝依賴套件
pip install -r requirements.txt
```

> **注意**：`webdriver-manager` 會在首次執行時自動下載 ChromeDriver。

### 3. 執行爬蟲

```bash
python nhi_scraper.py
```

### 4. 輸出結果
資料會自動儲存於 `data/` 目錄：
*   **單次快照 (CSV)**: `data/medical_centers_{YYYYMMDD_HHMMSS}.csv`
*   **單次快照 (JSON)**: `data/medical_centers_{YYYYMMDD_HHMMSS}.json`
*   **歷史累積**: `data/medical_centers_history.json` (所有歷史數據)

---

## 設定說明 (`config.py`)

您可以在 `config.py` 中調整各項參數：

*   **SELENIUM_CONFIG**: 設定 Headless 模式、等待超時等。
*   **SCRAPER_CONFIG**: 設定每頁顯示筆數、重試次數。
*   **EMAIL_CONFIG**: 設定 SMTP 伺服器、帳號密碼及收件人。

### Email 通知設定範例
若需開啟通知功能，請修改 `config.py`：

```python
EMAIL_CONFIG = {
    "enabled": True,                   # ⚠️ 務必改為 True 才能啟用
    "smtp_server": "smtp.gmail.com",   # Gmail 設定範例
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",  # 應用程式密碼
    "receiver_emails": ["receiver@example.com"],
    "subject_prefix": "[健保署爬蟲通知]",
}
```

### 測試 Email 設定
本專案提供測試工具，設定完成後可執行以下指令驗證：

```bash
python test_email_config.py
```

---

## 專案結構

```
健保署醫學中心爬蟲/
├── docs/                 # 專案文件
│   ├── DEPLOYMENT.md     # Windows 部署指南
│   ├── ROADMAP.md        # 開發路線圖
│   └── README.md         # 主要說明文件
├── data/                 # 資料儲存
│   ├── medical_centers_history.json  # 累積歷史資料
│   └── medical_centers_*.csv         # 單次抓取備份
├── logs/                 # 系統日誌
│   └── scraper.log       # 執行紀錄
├── nhi_scraper.py        # 核心爬蟲程式
├── config.py             # 設定檔 (含 Email 設定)
├── requirements.txt      # Python 依賴
└── run_scraper.bat       # Windows 自動執行腳本
```

---

## 相關文件

*   **[Windows 部署指南 (DEPLOYMENT.md)](DEPLOYMENT.md)**: 詳細的 Windows 環境架設、工作排程器設定與故障排除指南。
*   **[開發路線圖 (ROADMAP.md)](ROADMAP.md)**: 專案的開發階段規劃與未來展望。

---

## 資料欄位對照

| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| 醫院簡稱 | 醫學中心名稱 | 臺大、林口長庚 等 |
| 住院等待人數 | 等待住院的病患數 | 81 |
| 看診等待人數 | 等待門診的病患數 | 5 |
| 推床等待人數 | 使用推床的病患數 | 38 |
| 加護病房等待人數 | 等待加護病房的病患數 | 13 |
| 滿床通報狀態 | 是否已向119通報滿床 | 是/否 |
| 抓取時間 | 資料抓取的時間戳記 | 2026-02-10 12:33:42 |

---

## 疑難排解 (FAQ)

### Q: 出現 `ModuleNotFoundError`？
**A:** 請確認您已啟動虛擬環境並安裝了 `requirements.txt`。

### Q: 執行成功但沒有資料？
**A:** 可能是健保署網站維護或結構變更。請嘗試在 `config.py` 將 `headless` 設為 `False` 觀察瀏覽器行為，或查看 `logs/scraper.log`。

### Q: 如何設定 Windows 排程？
**A:** 請參考 [DEPLOYMENT.md](DEPLOYMENT.md) 中的詳細步驟。

---

**聯絡人**: Kevin Tsai
**授權**: 本專案僅供學習與研究使用，請遵守網站使用條款。
