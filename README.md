# 健保署醫學中心爬蟲 (NHI Medical Center Scraper)

> **專案狀態**: Production Ready (v4.0 - Serverless Dashboard)  
> **最新更新**: 2026-02-16  
> **技術核心**: GitHub Actions, GitHub Pages, Python, Chart.js, Serverless

## 專案概述

本專案是一個全自動化的**醫學中心急診戰情室**。透過 GitHub Actions 每日定時抓取健保署即時數據，並自動佈署至 GitHub Pages，提供全台 28 家醫學中心的急診等待人數視覺化監控。

**主要功能：**
*   **全自動雲端運行**: 每日 09:00 與 16:00 自動執行爬蟲 (GitHub Actions)，無需本地伺服器。
*   **Serverless 資料庫**: 使用 `data.js` 作為輕量級資料儲存，前端直接讀取，零資料庫維護成本。
*   **即時戰情室**:
    *   **紅燈警示**: 自動標記「滿床通報」與「等待人數 > 30」的緊急醫院。
    *   **趨勢分析**: 提供近 14 日的早晨住院等待人數趨勢圖。
    *   **RWD 設計**: 支援手機與桌機的響應式網頁 (Dark Mode)。
*   **混合模式**: 支援本地開發 (Docker + PostgreSQL) 與雲端部署 (GitHub Actions + File-based) 雙模式切換。

**資料來源**: [健保署特約醫療院所資訊查詢](https://info.nhi.gov.tw/INAE4000/INAE4001S01)
**線上預覽**: [點擊查看即時戰情室](https://aurnestea.github.io/nhi_emergency/) (請替換為您的實際 Pages 網址)

---

## 快速開始 (GitHub Actions 全自動模式)

本專案已設定好 CI/CD 流程，**您不需要在本地執行任何指令**即可運作。

### 1. 啟用 GitHub Pages
1. 進入 GitHub Repository 的 **Settings** > **Pages**。
2. 在 **Branch** 選擇 `main` (或 `master`) 並儲存。
3. 等待幾分鐘後，GitHub 會提供您的專案網址。

### 2. 啟用 Actions
專案內建 `.github/workflows/update_data.yml`，預設會每天自動執行。
*   您可以到 **Actions** 頁籤手動觸發 `Run workflow` 來測試。

### 3. 查看結果
開啟您的 GitHub Pages 網址，即可看到最新的急診等待數據。

---

## 本地開發 (Docker)

如果您需要修改程式碼或在本機測試：

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
