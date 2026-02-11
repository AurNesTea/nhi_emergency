@echo off
chcp 65001
echo ===========================================
echo 正在執行健保署醫學中心爬蟲...
echo 時間: %date% %time%
echo ===========================================

:: 切換到批次檔所在目錄
cd /d "%~dp0"

:: 檢查虛擬環境是否存在
if exist ".venv\Scripts\python.exe" (
    echo 使用 .venv 虛擬環境執行...
    ".venv\Scripts\python.exe" nhi_scraper.py
) else if exist "venv\Scripts\python.exe" (
    echo 使用 venv 虛擬環境執行...
    "venv\Scripts\python.exe" nhi_scraper.py
) else (
    echo 找不到虛擬環境 (.venv 或 venv)，嘗試使用系統 Python...
    python nhi_scraper.py
)

if %errorlevel% neq 0 (
    echo [錯誤] 爬蟲執行失敗！
    pause
    exit /b %errorlevel%
)

echo [成功] 執行完畢
echo ===========================================
timeout /t 5
