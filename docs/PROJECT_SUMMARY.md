# 專案總結 (Project Summary)

> **版本**: v5.1 (Data Sync & Maintenance)  
> **更新日期**: 2026-03-06

## 1. 專案現況
本專案已完成從單一腳本到 MVC 架構的轉型，目前支援多種部署模式，並具備高擴充性。

### 核心架構
- **Entry Point**: `main.py`
- **Source Code**: `src/`
    - **Scraper**: `src/nhi_scraper.py` (負責爬取)
    - **Services**: `src/services/` (Data Export, Email Notification)
    - **Models**: `src/models/` (SQLAlchemy ORM)
- **Configuration**: `src/config.py` (統一管理環境變數)

### 部署模式
1.  **GitHub Actions (Serverless) - [已驗證通過 ✅]**
    - 全自動每日爬取 (09:00, 16:00)
    - 資料儲存於 `data.js` 與 `data/` 歷史資料夾 (Git GitOps)
    - 前端透過 GitHub Pages 託管：[線上連結](https://aurnestea.github.io/nhi_emergency/)
    - **特別紀錄**: 已修正 `.gitignore` 以追蹤 `src/config.py` 與歷史資料，確保 CI/CD 環境完整。
2.  **Docker (Container)**
    - 包含 PostgreSQL 資料庫
    - 適合本地開發與完整資料保存
3.  **Windows (Local)**
    - 透過工作排程器 (Task Scheduler) 執行 `run_scraper.bat`

## 2. 最近變更
- **新聞嵌入支援 (v5.2)**: 新增 `embed_chart.html` 提供乾淨、自適應的圖表介面供新聞稿件嵌入 (iframe)，並支援自訂天數篩選 (7/14/28天)、過濾圖例及清爽的淺色佈景。同時清理移除了多餘的 `temp_data` 歷史目錄 (2026-03-06)。
- **資料維護 (v5.1)**: 完成將 `temp_data` 中的未建檔紀錄同步至前端 `data.js`，成功補齊自 2026 年 2 月起的 29 筆歷史時段，確保 14 日趨勢圖資料的完整性 (2026-03-06)。
- **目錄結構優化**: 將散落在根目錄的 Python 腳本移至 `src/`，保持根目錄整潔。
- **單一職責**: 拆分 `EmailService` 與 `DataService`，降低耦合度。
- **通用腳本**: 優化 `run_scraper.bat`，不再綁定絕對路徑，支援多人協作。

## 3. 下一步計畫
- **持續監控**: 觀察 GitHub Actions 執行穩定性。
- **前端優化**: 預計在 v6.0 引入更豐富的圖表與歷史資料查詢介面。
