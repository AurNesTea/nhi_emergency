# 專案開發路線圖 (Roadmap)

## 第一階段：核心爬蟲功能 (Completed)
- [x] 完成 `nhi_scraper.py` 核心邏輯
- [x] 實現無頭瀏覽器 (Headless Chrome) 自動化
- [x] 優化抓取效能 (全台資料一次抓取，~13秒)
- [x] 輸出 CSV 與 JSON 格式
- [x] 建立完整文件 (README.md)

## 第二階段:自動化與通知 (Completed)
> **完成日期**: 2026-02-10  
> **目標**: 實現無人值守的自動化運行,並建立資料累積機制與通知系統。

### 1. 定時排程 (Scheduling)
- [x] 建立 Windows 排程腳本 (`run_scraper.bat`)
- [x] 提供工作排程器設定指南 (詳見 `docs/DEPLOYMENT.md`)
- [x] 執行時間:每日 **09:00** 與 **16:00** (已於 Windows 10 環境驗證)

### 2. 資料累積 (Data Accumulation)
- [x] 建立「歷史資料庫」機制 (`medical_centers_history.json`)
- [x] 每次抓取後,將新資料追加 (Append) 到歷史檔案中
- [x] 確保資料格式一致性,包含時間戳記

### 3. Email 通知系統
- [x] 開發郵件發送模組
- [x] 支援 SMTP 設定 (Gmail / Outlook / 公司郵件伺服器)
- [x] 自動夾帶當次抓取的 CSV 檔案作為附件
- [x] 發送給指定收件人列表
- [x] 建立設定驗證工具 (`test_email_config.py`)

### 4. 錯誤處理強化 (新增)
- [x] 實作重試機制 (最多 3 次,間隔 2 秒)
- [x] 資料驗證功能 (確保抓取 28 筆醫學中心)
- [x] 詳細錯誤日誌記錄

## 第三階段：資料庫整合 (Completed - v3.0)
> **完成日期**: 2026-02-13
> **目標**: 引入 ORM 架構與 PostgreSQL 資料庫，建立穩健的資料儲存層。

### 1. 資料庫建置 (ORM Architecture)
- [x] 引入 ORM (SQLAlchemy)
- [x] 設計資料庫模型 (`models.py`)
- [x] 實作 PostgreSQL 連線邏輯 (`database.py`)
- [x] 容器化部署 (Docker + docker-compose)

## 第四階段：前端視覺化 (Future)
> 目標：建立現代化的網頁介面與資訊儀表板。

### 2. 前端視覺化 (Dashboard)
- [ ] 設計資訊儀表板 (Dashboard)
- [ ] 視覺化呈現：
    - 各醫院即時等待人數長條圖
    - 北中南東區域負載熱圖
    - 歷史趨勢圖 (Trend Analysis)
- [ ] 技術選型：現代化 Web 框架 (React/Vue 或 Python Based Dashboard)
