@echo off
chcp 65001
:: 1. 強制切換到 D 磁碟與專案目錄
d:
cd "D:\Kevin\nhi_emergency"

echo ===========================================
echo 正在執行健保署醫學中心爬蟲...
echo 工作目錄: %cd%
echo 時間: %date% %time%
echo ===========================================

:: 2. 直接使用完整路徑執行 (這是最穩且不會跳過的方法)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)

:: 3. 檢查執行結果
if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 爬蟲執行失敗！錯誤碼: %errorlevel%
    echo -------------------------------------------
    echo 可能原因：
    echo 1. .venv\Scripts\python.exe 這個檔案不存在
    echo 2. 爬蟲代碼內部出錯 (請看上方追蹤訊息)
    echo -------------------------------------------
    pause
    exit /b %errorlevel%
)

echo [成功] 執行完畢
echo ===========================================
timeout /t 10