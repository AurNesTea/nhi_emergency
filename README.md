# 健保署醫學中心爬蟲 (NHI Medical Center Scraper)

> **專案狀態**: Production Ready (v3.0 - Database & Docker Support)  
> **最新更新**: 2026-02-13  
> **技術核心**: Python 3.10, Selenium, PostgreSQL, Docker

## 專案概述

本專案旨在自動化抓取健保署網站上全台 28 家醫學中心的即時等待人數資料，並支援自動化排程、Email 通知與資料庫長期儲存。

**主要功能：**
*   **高效爬蟲**: 使用 Selenium + Headless Chrome，支援自動重試與錯誤隔離。
*   **混合儲存**:
    *   **資料庫**: 透過 SQLAlchemy ORM 寫入 PostgreSQL，適合長期分析。
    *   **檔案備份**: 保留 CSV 與 JSON 格式的單次快照。
*   **容器化部署**: 提供 `Dockerfile` 與 `docker-compose.yml`，一鍵啟動所有服務 (App + DB)。
*   **模組化架構**: 分離基礎建設 (`database.py`) 與業務模型 (`models.py`)，便於擴充。
*   **Email 通知**: 抓取完成後自動寄送報表，即使資料庫連線失敗也能獨立運作。

**資料來源**: [健保署特約醫療院所資訊查詢](https://info.nhi.gov.tw/INAE4000/INAE4001S01)

---

## 快速開始 (推薦使用 Docker)

這是最簡單的部署方式，無需在本機安裝 Python 或 Chrome。

### 1. 環境需求
*   Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)

### 2. 啟動服務

```bash
# 下載專案
git clone [repository_url]
cd nhi_emergency

# 啟動服務 (背景執行)
docker-compose up -d --build
```

此指令將自動：
1.  啟動 PostgreSQL 資料庫 (主機埠 5432)
2.  建置並啟動爬蟲容器
3.  自動執行第一次抓取
4.  將資料與日誌掛載回本機 (`data/` 與 `logs/`)

### 3. 查看狀態

```bash
# 查看爬蟲日誌
docker-compose logs -f scraper

# 檢查資料庫內容
docker-compose exec db psql -U postgres -d nhi_emergency -c "SELECT * FROM medical_center_records ORDER BY id DESC LIMIT 5;"
```

---

## 傳統部署 (Windows/Mac 本機執行)

若不使用 Docker，請參考以下步驟：

### 1. 安裝與設定
```bash
# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安裝依賴 (包含 selenium, sqlalchemy, psycopg2)
pip install -r requirements.txt
```

### 2. 資料庫設定 (選用)
若需寫入資料庫，請確保本機有 PostgreSQL 服務，並設定 `.env` 或環境變數。若無資料庫，程式會自動略過寫入步驟，僅產出 CSV。

### 3. 執行爬蟲
```bash
python nhi_scraper.py
```

---

## 專案結構

```
nhi_emergency/
├── data/                 # 資料輸出 (CSV/JSON)
├── logs/                 # 系統日誌
├── docs/                 # 專案文件
├── utils/                # 工具腳本 (如 Email 測試)
├── database.py           # 資料庫連線模組
├── models.py             # 資料庫模型定義
├── nhi_scraper.py        # 核心爬蟲程式
├── config.py             # 設定檔
├── Dockerfile            # 容器定義
├── docker-compose.yml    # 服務編排
└── requirements.txt      # Python 依賴
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
