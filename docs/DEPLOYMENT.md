# Windows 部署指南

> **目標環境**: Windows 10/11  
> **部署時間**: 約 15-20 分鐘  
> **技術需求**: Python 3.8+, Chrome 瀏覽器

---

## 部署前準備

### 1. 確認系統需求

- [x] Windows 10 或 Windows 11
- [x] Google Chrome 瀏覽器 (最新版本)
- [x] 網路連線 (用於下載 Python 套件)
- [x] 系統管理員權限 (用於設定工作排程器)

### 2. 安裝 Python

1. 前往 [Python 官網](https://www.python.org/downloads/) 下載 Python 3.10 或更新版本
2. **重要**: 安裝時勾選 "Add Python to PATH"
3. 驗證安裝:
   ```cmd
   python --version
   ```
   應顯示: `Python 3.10.x` 或更高版本

---

## 部署步驟

### Step 1: 複製專案檔案

將整個專案資料夾複製到 Windows 電腦,建議路徑:
```
C:\Projects\nhi_emergency\
```

### Step 2: 建立虛擬環境

開啟 **命令提示字元 (CMD)** 或 **PowerShell**,切換到專案目錄:

```cmd
cd C:\Projects\nhi_emergency
python -m venv venv
```

### Step 3: 啟動虛擬環境並安裝依賴

```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

> **注意**: 如果出現 SSL 錯誤,可使用:
> ```cmd
> pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
> ```

### Step 4: 測試執行

```cmd
python nhi_scraper.py
```

預期結果:
- 成功抓取 28 筆醫學中心資料
- 生成 CSV 和 JSON 檔案於 `data/` 目錄
- 執行時間約 10-15 秒

---

## Email 通知設定 (選用)

### Gmail 設定範例

1. 開啟 `config.py`,修改 `EMAIL_CONFIG`:

```python
EMAIL_CONFIG = {
    "enabled": True,  # 改為 True 啟用
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",  # 您的 Gmail
    "sender_password": "xxxx xxxx xxxx xxxx",  # 應用程式密碼
    "receiver_emails": ["receiver@example.com"],  # 收件者列表
    "subject_prefix": "[健保署爬蟲通知]",
}
```

### 取得 Gmail 應用程式密碼

1. 登入 [Google 帳戶](https://myaccount.google.com/)
2. 前往 **安全性** → **兩步驟驗證** (必須先啟用)
3. 點選 **應用程式密碼**
4. 選擇「郵件」和「Windows 電腦」
5. 複製產生的 16 位密碼 (格式: `xxxx xxxx xxxx xxxx`)
6. 貼到 `config.py` 的 `sender_password` 欄位

### Outlook/公司郵件設定

```python
EMAIL_CONFIG = {
    "enabled": True,
    "smtp_server": "smtp.office365.com",  # Outlook
    "smtp_port": 587,
    "sender_email": "your_email@company.com",
    "sender_password": "your_password",
    "receiver_emails": ["receiver@company.com"],
    "subject_prefix": "[健保署爬蟲通知]",
}
```

### 驗證 Email 設定 (推薦)

設定完成後，建議先執行測試腳本確認連線正常：

```cmd
python test_email_config.py
```

若看到 `[+] 成功！測試郵件已發送`，即可繼續下一步。

---

## 設定 Windows 工作排程器

### 方法一: 使用圖形介面 (建議)

#### 1. 開啟工作排程器
- 按 `Win + R`,輸入 `taskschd.msc`,按 Enter

#### 2. 建立基本工作
1. 點選右側 **「建立基本工作」**
2. 名稱: `nhi_emergency - 早上`
3. 描述: `每日 09:00 自動抓取醫學中心資料`
4. 點選 **下一步**

#### 3. 設定觸發程序
1. 選擇 **「每天」**
2. 開始時間: `09:00:00`
3. 點選 **下一步**

#### 4. 設定動作
1. 選擇 **「啟動程式」**
2. 程式或指令碼: 瀏覽並選擇 `run_scraper.bat`
   - 完整路徑範例: `C:\Projects\nhi_emergency\run_scraper.bat`
3. 點選 **下一步** → **完成**

#### 5. 重複步驟建立下午排程
- 名稱: `nhi_emergency - 下午`
- 時間: `16:00:00`

### 方法二: 使用命令列 (進階)

開啟 **系統管理員權限的 CMD**,執行:

```cmd
:: 早上 09:00 排程
schtasks /create /tn "健保署爬蟲-早上" /tr "C:\Projects\nhi_emergency\run_scraper.bat" /sc daily /st 09:00

:: 下午 16:00 排程
schtasks /create /tn "健保署爬蟲-下午" /tr "C:\Projects\nhi_emergency\run_scraper.bat" /sc daily /st 16:00
```

### 驗證排程設定

1. 在工作排程器中找到剛建立的工作
2. 右鍵點選 → **執行**
3. 檢查 `data/` 目錄是否有新的 CSV/JSON 檔案
4. 檢查 `logs/scraper.log` 確認執行狀態

---

## 檔案結構說明

```
C:\Projects\nhi_emergency\
├── nhi_scraper.py              # 主程式
├── config.py                   # 設定檔 (Email, 重試次數等)
├── requirements.txt            # Python 依賴套件
├── run_scraper.bat             # Windows 執行腳本
├── data/                       # 資料輸出目錄
│   ├── medical_centers_history.json  # 歷史累積資料
│   └── medical_centers_*.csv         # 每次執行的快照
└── logs/                       # 日誌目錄
    └── scraper.log             # 執行日誌
```

---

## 常見問題排除

### Q1: 執行時出現 `ModuleNotFoundError`

**原因**: 虛擬環境未啟動或套件未安裝

**解決方法**:
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Q2: ChromeDriver 版本不符

**原因**: Chrome 瀏覽器版本與 ChromeDriver 不匹配

**解決方法**:
```cmd
pip install --upgrade webdriver-manager
```

### Q3: 工作排程器執行失敗

**檢查項目**:
1. 確認 `run_scraper.bat` 路徑正確
2. 確認虛擬環境已建立 (`venv\Scripts\python.exe` 存在)
3. 查看 `logs\scraper.log` 錯誤訊息
4. 手動執行 `run_scraper.bat` 測試

### Q4: Email 發送失敗

**檢查項目**:
1. SMTP 伺服器和連接埠正確
2. Gmail 應用程式密碼正確 (不是 Google 帳戶密碼)
3. 收件者 Email 格式正確
4. 網路防火牆未阻擋 SMTP 連線 (Port 587)

### Q5: 抓取資料不完整 (< 28 筆)

**可能原因**:
1. 健保署網站暫時維護
2. 網路連線不穩定
3. 網站結構變更

**解決方法**:
- 程式會自動重試 3 次 (可在 `config.py` 調整)
- 檢查 `logs\scraper.log` 查看詳細錯誤
- 設定 `config.py` 中 `headless: False` 觀察瀏覽器行為

---

## 監控與維護

### 檢查執行狀態

1. **查看最新日誌**:
   ```cmd
   type logs\scraper.log
   ```

2. **檢查資料檔案**:
   ```cmd
   dir data\*.csv /o-d
   ```

3. **驗證歷史資料**:
   ```cmd
   python -m json.tool data\medical_centers_history.json
   ```

### 定期維護建議

- **每週**: 檢查 `logs\scraper.log` 確認無錯誤
- **每月**: 清理舊的 CSV 檔案 (保留 `medical_centers_history.json`)
- **每季**: 更新 Python 套件:
  ```cmd
  pip install --upgrade -r requirements.txt
  ```

---

## 技術支援

如遇到無法解決的問題,請提供以下資訊:

1. Windows 版本 (`winver` 查詢)
2. Python 版本 (`python --version`)
3. Chrome 版本 (開啟 Chrome → 設定 → 關於 Chrome)
4. 完整錯誤訊息 (從 `logs\scraper.log`)
5. 執行截圖

**聯絡人**: Kevin Tsai  
**專案版本**: v1.0 (Phase 2)

---

## 部署檢查清單

部署完成後,請確認以下項目:

- [ ] Python 已安裝並加入 PATH
- [ ] 虛擬環境已建立並啟動
- [ ] 所有依賴套件已安裝
- [ ] 手動執行測試成功 (抓取 28 筆資料)
- [ ] Email 通知功能測試成功 (如有啟用)
- [ ] 工作排程器已設定 (09:00 和 16:00)
- [ ] 排程測試執行成功
- [ ] 日誌檔案正常記錄

**恭喜!部署完成!**
