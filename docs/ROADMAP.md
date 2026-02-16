# 專案開發路線圖 (Roadmap)

## 第一階段：核心爬蟲功能 (Completed)

- [X] 完成 `nhi_scraper.py` 核心邏輯
- [X] 實現無頭瀏覽器 (Headless Chrome) 自動化
- [X] 優化抓取效能 (全台資料一次抓取，~13秒)
- [X] 輸出 CSV 與 JSON 格式
- [X] 建立完整文件 (README.md)

## 第二階段:自動化與通知 (Completed)

> **完成日期**: 2026-02-10
> **目標**: 實現無人值守的自動化運行,並建立資料累積機制與通知系統。

### 1. 定時排程 (Scheduling)

- [X] 建立 Windows 排程腳本 (`run_scraper.bat`)
- [X] 提供工作排程器設定指南 (詳見 `docs/DEPLOYMENT.md`)
- [X] 執行時間:每日 **09:00** 與 **16:00** (已於 Windows 10 環境驗證)

### 2. 資料累積 (Data Accumulation)

- [X] 建立「歷史資料庫」機制 (`medical_centers_history.json`)
- [X] 每次抓取後,將新資料追加 (Append) 到歷史檔案中
- [X] 確保資料格式一致性,包含時間戳記

### 3. Email 通知系統

- [X] 開發郵件發送模組
- [X] 支援 SMTP 設定 (Gmail / Outlook / 公司郵件伺服器)
- [X] 自動夾帶當次抓取的 CSV 檔案作為附件
- [X] 發送給指定收件人列表
- [X] 建立設定驗證工具 (`test_email_config.py`)

### 4. 錯誤處理強化 (新增)

- [X] 實作重試機制 (最多 3 次,間隔 2 秒)
- [X] 資料驗證功能 (確保抓取 28 筆醫學中心)
- [X] 詳細錯誤日誌記錄

## 第三階段：資料庫整合 (Completed - v3.0)

> **完成日期**: 2026-02-13
> **目標**: 引入 ORM 架構與 PostgreSQL 資料庫，建立穩健的資料儲存層。

### 1. 資料庫建置 (ORM Architecture)

- [X] 引入 ORM (SQLAlchemy)
- [X] 設計資料庫模型 (`models.py`)
- [X] 實作 PostgreSQL 連線邏輯 (`database.py`)
- [X] 容器化部署 (Docker + docker-compose)

## 第四階段：前端視覺化 (Completed - v4.0)

> **完成日期**: 2026-02-16
> **目標**: 建立現代化的網頁介面與資訊儀表板。

### 1. 資訊儀表板 (Dashboard)

- [X] 設計深色主題戰情室 (Dark Mode Dashboard)
- [X] 視覺化呈現：
  - [X] 即時告警卡片 (紅燈/黃燈/綠燈機制)
  - [X] 全台 28 家醫學中心網格概覽
  - [X] 近 14 日早晨住院等待趨勢圖 (Chart.js)
- [X] 自動化部署 (GitHub Pages)

## 第五階段：架構重構 (Completed - v5.0)

> **完成日期**: 2026-02-17
> **目標**: 導入 MVC 架構與模組化設計

### 1. 程式碼重構

- [X] 建立 `src/` 目錄結構
- [X] 拆分 `models`, `services` 模組
- [X] 統一入口點 `main.py`
- [X] 優化 GitHub Actions Workflow 並驗證通過 (2026-02-17)

## 第六階段：未來可做功能 (Future)

### 1. 資料存取增強

- [ ] Google Sheets 整合 (作為簡易資料庫與協作介面)
- [ ] API 開發 (提供 JSON API 供第三方串接)

### 2. 進階圖表

- [ ] 北中南東區域負載熱圖
- [ ] 預測模型 (預測未來一週的急診高峰)
