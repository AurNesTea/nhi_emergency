@echo off
chcp 65001
echo ===========================================
echo [Docker] 正在啟動健保署醫學中心爬蟲...
echo 時間: %date% %time%
echo ===========================================

:: 切換到批次檔所在目錄 (專案根目錄)
cd /d "%~dp0"

:: 使用 Docker Compose 執行爬蟲服務
:: --rm: 執行完畢後自動移除暫時性容器，保持環境乾淨
:: scraper: 指定只執行 scraper 這個服務 (會自動啟動相依的 db)
docker-compose run --rm scraper

if %errorlevel% neq 0 (
    echo [錯誤] 爬蟲執行失敗 (Docker Exit Code: %errorlevel%)
    pause
    exit /b %errorlevel%
)

echo [成功] 執行完畢
echo ===========================================
timeout /t 5
