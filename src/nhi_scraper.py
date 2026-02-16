# 專案目錄加入路徑
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import logging
from datetime import datetime
from pathlib import Path
from functools import wraps

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from src.config import (
    TARGET_URL, 
    SELENIUM_CONFIG, 
    SCRAPER_CONFIG, 
    get_output_filename,
    LOG_FILE
)

# 移除重複的 logging config，統一在進入點或 config 設定即可
# 但為了開發測試方便，若沒有 logger handler 則補上
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def retry_on_failure(max_retries=None, delay=None):
    """
    重試裝飾器：當函數執行失敗時自動重試
    """
    if max_retries is None:
        max_retries = SCRAPER_CONFIG['retry_times']
    if delay is None:
        delay = SCRAPER_CONFIG['retry_delay']
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} 執行失敗 (第 {attempt + 1}/{max_retries} 次重試): {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} 已達最大重試次數，放棄執行")
                except Exception as e:
                    logger.error(f"{func.__name__} 發生非預期錯誤: {e}")
                    raise
            raise last_exception
        
        return wrapper
    return decorator


class NHIMedicalCenterScraper:
    """健保署醫學中心資料爬蟲"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.driver = None
        self.data = []
        
    def setup_driver(self):
        """設定 Chrome WebDriver"""
        logger.info("正在初始化 Chrome WebDriver...")
        
        chrome_options = Options()
        
        # 無頭模式
        if SELENIUM_CONFIG['headless']:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
        
        # 其他優化選項
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            import os
            # GitHub Actions 環境強制使用 headless
            if os.environ.get('GITHUB_ACTIONS'):
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')

            chrome_bin = os.environ.get('CHROME_BIN')
            chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')

            if chrome_bin and chromedriver_path:
                logger.info(f"使用系統內建 Chromium: {chrome_bin}")
                chrome_options.binary_location = chrome_bin
                service = Service(chromedriver_path)
            else:
                driver_path = ChromeDriverManager().install()
                basename = os.path.basename(driver_path)
                expected_names = ['chromedriver', 'chromedriver.exe']
                
                if basename.lower() not in expected_names:
                    driver_dir = os.path.dirname(driver_path)
                    for root, dirs, files in os.walk(driver_dir):
                        for filename in files:
                            if filename.lower() in expected_names:
                                driver_path = os.path.join(root, filename)
                                break
                                
                if os.name != 'nt':
                    os.chmod(driver_path, 0o755)
                
                service = Service(driver_path)

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(SELENIUM_CONFIG['page_load_timeout'])
            logger.info("WebDriver 初始化完成")
            
        except Exception as e:
            logger.error(f"WebDriver 初始化失敗: {e}")
            raise
    
    @retry_on_failure()
    def navigate_to_page(self):
        logger.info(f"正在訪問網站: {TARGET_URL}")
        self.driver.get(TARGET_URL)
        time.sleep(3)
        logger.info("頁面載入完成")
    
    def select_medical_center(self):
        logger.info("正在選擇院所層級：醫學中心")
        try:
            wait = WebDriverWait(self.driver, SELENIUM_CONFIG['wait_timeout'])
            selects = self.driver.find_elements(By.TAG_NAME, 'select')
            
            if len(selects) >= 2:
                level_select = selects[1]
                level_select.click()
                time.sleep(1)
                
                options = level_select.find_elements(By.TAG_NAME, 'option')
                for option in options:
                    if '醫學中心' in option.text:
                        option.click()
                        logger.info("已選擇「醫學中心」")
                        time.sleep(1)
                        break
            else:
                logger.error("找不到院所層級下拉選單")
        except Exception as e:
            logger.error(f"選擇院所層級時發生錯誤: {e}")
            raise
    
    def set_records_per_page(self):
        try:
            records_per_page = SCRAPER_CONFIG['records_per_page']
            logger.info(f"設定每頁顯示 {records_per_page} 筆")
            
            selects = self.driver.find_elements(By.TAG_NAME, 'select')
            if len(selects) >= 3:
                records_select = selects[2]
                records_select.click()
                time.sleep(0.5)
                
                options = records_select.find_elements(By.TAG_NAME, 'option')
                for option in options:
                    if str(records_per_page) in option.text:
                        option.click()
                        logger.info(f"已設定每頁顯示 {records_per_page} 筆")
                        time.sleep(0.5)
                        break
        except Exception as e:
            logger.warning(f"設定每頁顯示筆數時發生錯誤（繼續執行）: {e}")
    
    @retry_on_failure()
    def click_search_button(self):
        logger.info("正在點擊查詢按鈕...")
        wait = WebDriverWait(self.driver, SELENIUM_CONFIG['wait_timeout'])
        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-l")))
        logger.info("找到查詢按鈕")
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", search_button)
        logger.info("已點擊查詢按鈕")
        time.sleep(3)
    
    @retry_on_failure()
    def scrape_table_data(self):
        logger.info("正在抓取表格資料...")
        wait = WebDriverWait(self.driver, SELENIUM_CONFIG['wait_timeout'])
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        
        rows = table.find_elements(By.TAG_NAME, 'tr')
        logger.info(f"找到 {len(rows)} 列資料")
        data_rows = rows[1:] if len(rows) > 1 else []
        
        for row in data_rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 6:
                record = {
                    '醫院簡稱': cells[0].text.strip(),
                    '住院等待人數': cells[1].text.strip(),
                    '看診等待人數': cells[2].text.strip(),
                    '推床等待人數': cells[3].text.strip(),
                    '加護病房等待人數': cells[4].text.strip(),
                    '滿床通報狀態': cells[5].text.strip(),
                    '抓取時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.data.append(record)
        logger.info(f"成功抓取 {len(data_rows)} 筆醫學中心資料")
    
    def validate_data(self):
        expected_count = 28
        actual_count = len(self.data)
        
        if actual_count == 0:
            logger.error("資料驗證失敗：未抓取到任何資料")
            raise ValueError("未抓取到任何醫學中心資料")
        
        if actual_count < expected_count:
            logger.warning(f"資料驗證警告：預期 {expected_count} 筆，實際抓取 {actual_count} 筆")
        elif actual_count == expected_count:
            logger.info(f"資料驗證通過：成功抓取完整的 {actual_count} 筆資料")
        
        return actual_count >= expected_count * 0.8
    
    def save_to_csv(self):
        if not self.data: return None
        df = pd.DataFrame(self.data)
        output_file = get_output_filename('csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"CSV 檔案已儲存: {output_file}")
        return output_file
    
    def save_to_json(self):
        if not self.data: return None
        df = pd.DataFrame(self.data)
        output_file = get_output_filename('json')
        df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        logger.info(f"JSON 檔案已儲存: {output_file}")
        return output_file
    
    def save_to_database(self):
        if not self.data: return
        logger.info("正在將資料寫入資料庫...")
        try:
            from src.models.database import SessionLocal, init_db
            from src.models.medical_center import MedicalCenterRecord
            
            try:
                init_db()
            except Exception as e:
                logger.warning(f"資料庫初始化警告: {e}")

            db = SessionLocal()
            try:
                for record in self.data:
                    is_full_bed = True if "是" in record.get('滿床通報狀態', '') else False
                    
                    def parse_int(value):
                        try: return int(value)
                        except: return 0

                    db_record = MedicalCenterRecord(
                        hospital_name=record.get('醫院簡稱'),
                        inpatient_waiting=parse_int(record.get('住院等待人數')),
                        outpatient_waiting=parse_int(record.get('看診等待人數')),
                        stretcher_waiting=parse_int(record.get('推床等待人數')),
                        icu_waiting=parse_int(record.get('加護病房等待人數')),
                        is_full_bed=is_full_bed,
                        created_at=datetime.strptime(record.get('抓取時間'), '%Y-%m-%d %H:%M:%S')
                    )
                    db.add(db_record)
                db.commit()
                logger.info(f"成功寫入 {len(self.data)} 筆資料至資料庫")
            except Exception as e:
                logger.error(f"寫入資料庫時發生錯誤: {e}")
                db.rollback()
            finally:
                db.close()
        except ImportError:
            logger.error("無法匯入資料庫模組")
        except Exception as e:
            logger.error(f"資料庫連線或操作失敗: {e}")

    def run(self):
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("開始執行健保署醫學中心資料爬蟲")
        logger.info("=" * 60)
        
        try:
            self.setup_driver()
            self.navigate_to_page()
            self.select_medical_center()
            self.set_records_per_page()
            self.click_search_button()
            self.scrape_table_data()
            is_valid = self.validate_data()
            
            csv_file = self.save_to_csv()
            json_file = self.save_to_json()
            
            import os
            
            # 使用新的 Email Service
            if csv_file and not os.environ.get('GITHUB_ACTIONS'):
                try:
                    from src.services.email_service import send_scraping_report
                    logger.info("正在發送 Email 通知...")
                    send_scraping_report(len(self.data), csv_file)
                except Exception as e:
                    logger.error(f"Email 發送失敗: {e}")
            else:
                logger.info("GitHub Actions 環境或無檔案：跳過發送 Email。")

            if not os.environ.get('GITHUB_ACTIONS'):
                self.save_to_database()
            else:
                logger.info("GitHub Actions 環境：跳過 PostgreSQL 寫入。")

            try:
                from src.services.data_service import export_to_web_data
                export_to_web_data(new_data=self.data)
            except Exception as e:
                logger.warning(f"更新前端資料失敗: {e}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"爬蟲執行完成！共抓取 {len(self.data)} 筆資料，耗時 {duration:.2f} 秒")
            return True
            
        except Exception as e:
            logger.error(f"爬蟲執行失敗: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("已關閉瀏覽器")


def main():
    scraper = NHIMedicalCenterScraper()
    success = scraper.run()
    
    if success:
        print("\n爬蟲執行成功！")
        print(f"資料已儲存至 {Path('data').absolute()}")
    else:
        print("\n爬蟲執行失敗，請查看日誌檔案")
        print(f"日誌位置: {LOG_FILE}")

if __name__ == "__main__":
    main()
