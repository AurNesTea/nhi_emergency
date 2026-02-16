
# 專案入口點
# 執行此程式將啟動爬蟲流程

import sys
import os

# 將專案根目錄加入 PYTHONPATH，確保可以正確 import src 模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.nhi_scraper import main as scraper_main

if __name__ == "__main__":
    print("啟動健保署醫學中心爬蟲...")
    scraper_main()
