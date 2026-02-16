# 專案文件 (Documentation)

| 檔案名稱 | 描述 |
| --- | --- |
| [README.md](../README.md) | 專案首頁，包含快速開始與專案概述 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 詳細部署指南 (GitHub/Docker/Windows) |
| [ROADMAP.md](ROADMAP.md) | 開發路線圖與版本歷史 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 專案架構總結與決策紀錄 |

## 最近更新 (v5.0 - Refactoring)
> **日期**: 2026-02-17

- **架構重構**: 採用 MVC pattern 重組程式碼
    - `src/`：核心邏輯目錄
    - `src/models/`：資料庫模型
    - `src/services/`：商業邏輯 (Data, Email)
    - `main.py`：新版統一入口點
- **GitHub Actions**: 更新 Workflow 以支援新架構
- **環境變數**: 引入 `python-dotenv` 增強安全性

## 舊版文件歸檔
(如需查看舊版架構請參考 Git History)
