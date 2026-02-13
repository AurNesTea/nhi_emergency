# 使用 Python 3.10 作為基礎映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 安裝系統依賴與 Chromium (支援 ARM64/AMD64)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libpq-dev \
    gcc \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 設定環境變數讓 Python 腳本抓到正確路徑
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案程式碼
COPY . .

# 建立必要的目錄
RUN mkdir -p data logs

# 設定預設指令
CMD ["python", "nhi_scraper.py"]
