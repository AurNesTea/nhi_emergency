"""
健保署醫學中心即時資料爬蟲

功能：
1. 抓取全國所有醫學中心的即時等待人數資料
2. 輸出為 CSV 和 JSON 格式
3. 包含完整的錯誤處理和日誌記錄

作者：Kevin Tsai
建立日期：2026-02-10
"""

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

from config import (
    TARGET_URL, 
    SELENIUM_CONFIG, 
    SCRAPER_CONFIG, 
    get_output_filename,
    LOG_FILE,
    HISTORY_FILE,
    EMAIL_CONFIG
)
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=None, delay=None):
    """
    重試裝飾器：當函數執行失敗時自動重試
    
    Args:
        max_retries: 最大重試次數（預設從 config 讀取）
        delay: 重試間隔秒數（預設從 config 讀取）
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
                    # 非預期的錯誤不重試，直接拋出
                    logger.error(f"{func.__name__} 發生非預期錯誤: {e}")
                    raise
            
            # 所有重試都失敗，拋出最後一次的異常
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
        
        # 自動下載並設定 ChromeDriver
        try:
            import os
            # 關鍵：如果在 GitHub Actions 環境，強制使用 headless
            if os.environ.get('GITHUB_ACTIONS'):
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')

            # 優先檢查環境變數 (Docker 環境)
            chrome_bin = os.environ.get('CHROME_BIN')
            chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')

            if chrome_bin and chromedriver_path:
                logger.info(f"使用系統內建 Chromium: {chrome_bin}")
                chrome_options.binary_location = chrome_bin
                service = Service(chromedriver_path)
            else:
                # 本機環境使用 webdriver-manager
                driver_path = ChromeDriverManager().install()
                
                # 修正路徑問題 (解決 Windows/Mac 可能抓到 LICENSE/NOTICE 檔案導致的 WinError 193)
                basename = os.path.basename(driver_path)
                
                # 檢查是否為正確的執行檔名稱
                expected_names = ['chromedriver', 'chromedriver.exe']
                if basename.lower() not in expected_names:
                    logger.warning(f"webdriver-manager 返回的路徑可能非執行檔: {driver_path}，嘗試搜尋實際執行檔...")
                    driver_dir = os.path.dirname(driver_path)
                    found = False
                    for root, dirs, files in os.walk(driver_dir):
                        for filename in files:
                            if filename.lower() in expected_names:
                                driver_path = os.path.join(root, filename)
                                found = True
                                break
                        if found:
                            break
                    
                    if found:
                        logger.info(f"已修正 ChromeDriver 路徑: {driver_path}")
                    else:
                        logger.error(f"在 {driver_dir} 中找不到 chromedriver 執行檔")

                # macOS/Linux 需要給予執行權限
                if os.name != 'nt':
                    os.chmod(driver_path, 0o755)
                
                service = Service(driver_path)

            # Service 初始化 (共用)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 設定超時時間
            self.driver.set_page_load_timeout(SELENIUM_CONFIG['page_load_timeout'])
            
            logger.info("WebDriver 初始化完成")
            
        except Exception as e:
            logger.error(f"WebDriver 初始化失敗: {e}")
            raise
    

    @retry_on_failure()  # 使用重試機制確保穩定性
    def navigate_to_page(self):
        """導航至目標網頁"""
        logger.info(f"正在訪問網站: {TARGET_URL}")
        self.driver.get(TARGET_URL)
        
        # 等待頁面載入完成
        time.sleep(3)
        logger.info("頁面載入完成")
    
    def select_medical_center(self):
        """選擇「醫學中心」選項"""
        logger.info("正在選擇院所層級：醫學中心")
        
        try:
            # 等待下拉選單出現
            wait = WebDriverWait(self.driver, SELENIUM_CONFIG['wait_timeout'])
            
            # 找到「院所層級」下拉選單 (通常是第二個 select)
            # 根據網站分析，可能需要點擊才會出現選項
            selects = self.driver.find_elements(By.TAG_NAME, 'select')
            
            if len(selects) >= 2:
                level_select = selects[1]  # 第二個選單是院所層級
                level_select.click()
                time.sleep(1)
                
                # 選擇「醫學中心」選項
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
        """設定每頁顯示筆數"""
        try:
            records_per_page = SCRAPER_CONFIG['records_per_page']
            logger.info(f"設定每頁顯示 {records_per_page} 筆")
            
            # 找到「每頁顯示筆數」下拉選單（通常是第三個 select）
            selects = self.driver.find_elements(By.TAG_NAME, 'select')
            
            if len(selects) >= 3:
                records_select = selects[2]
                records_select.click()
                time.sleep(0.5)
                
                # 選擇對應的筆數
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
        """點擊查詢按鈕"""
        logger.info("正在點擊查詢按鈕...")
        
        # 等待按鈕可點擊
        wait = WebDriverWait(self.driver, SELENIUM_CONFIG['wait_timeout'])
        
        # 直接使用 class 定位查詢按鈕（注意：btn-l 是小寫）
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-l"))
        )
        
        logger.info("找到查詢按鈕")
        
        # 確保按鈕可見並點擊
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
        time.sleep(0.5)
        
        # 使用 JavaScript 點擊（更可靠）
        self.driver.execute_script("arguments[0].click();", search_button)
        logger.info("已點擊查詢按鈕")
        
        # 等待結果載入
        time.sleep(3)
    
    @retry_on_failure()
    def scrape_table_data(self):
        """抓取表格資料"""
        logger.info("正在抓取表格資料...")
        
        # 等待表格出現
        wait = WebDriverWait(self.driver, SELENIUM_CONFIG['wait_timeout'])
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        
        # 取得所有資料列
        rows = table.find_elements(By.TAG_NAME, 'tr')
        logger.info(f"找到 {len(rows)} 列資料")
        
        # 解析表頭（用於確認欄位順序）
        headers = []
        if len(rows) > 0:
            header_cells = rows[0].find_elements(By.TAG_NAME, 'th')
            headers = [cell.text.strip() for cell in header_cells]
            logger.debug(f"表頭: {headers}")
        
        # 解析資料列
        data_rows = rows[1:] if len(rows) > 1 else []
        
        for row in data_rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            
            if len(cells) >= 6:  # 確保有足夠的欄位
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
        """驗證抓取的資料是否完整"""
        expected_count = 28  # 全國醫學中心總數
        actual_count = len(self.data)
        
        if actual_count == 0:
            logger.error("資料驗證失敗：未抓取到任何資料")
            raise ValueError("未抓取到任何醫學中心資料")
        
        if actual_count < expected_count:
            logger.warning(f"資料驗證警告：預期 {expected_count} 筆，實際抓取 {actual_count} 筆")
            logger.warning("可能原因：健保署網站資料不完整或網站結構變更")
        elif actual_count == expected_count:
            logger.info(f"資料驗證通過：成功抓取完整的 {actual_count} 筆資料")
        else:
            logger.warning(f"資料驗證警告：預期 {expected_count} 筆，實際抓取 {actual_count} 筆（超出預期）")
        
        return actual_count >= expected_count * 0.8  # 至少要有 80% 的資料才算通過
    
    def save_to_csv(self):
        """儲存為 CSV 檔案"""
        if not self.data:
            logger.warning("沒有資料可儲存")
            return None
        
        df = pd.DataFrame(self.data)
        output_file = get_output_filename('csv')
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"CSV 檔案已儲存: {output_file}")
        
        return output_file
    
    def save_to_json(self):
        """儲存為 JSON 檔案"""
        if not self.data:
            logger.warning("沒有資料可儲存")
            return None
        
        df = pd.DataFrame(self.data)
        output_file = get_output_filename('json')
        
        df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        logger.info(f"JSON 檔案已儲存: {output_file}")
        
        return output_file
    
    def save_to_database(self):
        """
        將資料寫入 PostgreSQL 資料庫
        此方法包含獨立的錯誤處理，確保不影響主程式流程
        """
        if not self.data:
            return

        logger.info("正在將資料寫入資料庫...")
        
        # 延遲匯入以避免循環引用或在無資料庫依賴環境下報錯
        try:
            from database import SessionLocal, init_db
            from models import MedicalCenterRecord
            
            # 嘗試初始化資料表（如果還沒建立）
            try:
                init_db()
            except Exception as e:
                logger.warning(f"資料庫初始化警告 (可能已存在或連線失敗): {e}")

            db = SessionLocal()
            try:
                for record in self.data:
                    # 轉換資料格式以符合模型
                    # 注意：record['滿床通報狀態'] 是 "是"/"否" 字串，需轉換為 Boolean
                    is_full_bed = True if "是" in record.get('滿床通報狀態', '') else False
                    
                    # 轉換數字欄位 (移除可能的非數字字符)
                    def parse_int(value):
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            return 0

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
            logger.error("無法匯入資料庫模組，請檢查是否已安裝 SQLAlchemy 與 psycopg2-binary")
        except Exception as e:
            logger.error(f"資料庫連線或操作失敗: {e}")

    def send_email(self, attachment_path):
        """發送 Email 通知"""
        if not EMAIL_CONFIG['enabled']:
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = ", ".join(EMAIL_CONFIG['receiver_emails'])
            msg['Subject'] = f"{EMAIL_CONFIG['subject_prefix']} 醫學中心等待人數資料 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            
            # 郵件內文
            body = f"""
            您好，
            
            這是自動發送的健保署醫學中心爬蟲報告。
            執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            抓取筆數：{len(self.data)} 筆
            
            詳細資料請參考附件 CSV 檔案。
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # 夾帶附件
            if attachment_path:
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=Path(attachment_path).name)
                part['Content-Disposition'] = f'attachment; filename="{Path(attachment_path).name}"'
                msg.attach(part)
            
            # 發送郵件
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                server.send_message(msg)
                
            logger.info(f"Email 通知已發送至: {', '.join(EMAIL_CONFIG['receiver_emails'])}")
            
        except Exception as e:
            logger.error(f"發送 Email 時發生錯誤: {e}")
    
    def run(self):
        """執行完整的爬蟲流程"""
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("開始執行健保署醫學中心資料爬蟲")
        logger.info("=" * 60)
        
        try:
            # 1. 設定 WebDriver
            self.setup_driver()
            
            # 2. 訪問網站
            self.navigate_to_page()
            
            # 3. 選擇「醫學中心」
            logger.info("正在選擇院所層級：醫學中心")
            self.select_medical_center()
            
            # 4. 設定每頁顯示筆數
            logger.info("正在設定每頁顯示筆數")
            self.set_records_per_page()
            
            # 5. 點擊查詢
            logger.info("正在執行查詢")
            self.click_search_button()
            
            # 6. 抓取表格資料
            logger.info("正在抓取所有醫學中心資料")
            self.scrape_table_data()
            
            # 7. 驗證資料完整性
            logger.info("正在驗證資料完整性")
            is_valid = self.validate_data()
            
            # 8. 儲存資料
            csv_file = self.save_to_csv()
            json_file = self.save_to_json()
            
            # 9. 發送 Email 通知 (檢測環境)
            if csv_file and not os.environ.get('GITHUB_ACTIONS'):
                logger.info("正在發送 Email 通知...")
                self.send_email(csv_file)
            elif os.environ.get('GITHUB_ACTIONS'):
                logger.info("GitHub Actions 環境：跳過發送 Email。")

            # 10. 寫入資料庫 (檢測環境)
            if not os.environ.get('GITHUB_ACTIONS'):
                logger.info("正在寫入資料庫...")
                self.save_to_database()
            else:
                logger.info("GitHub Actions 環境：跳過 PostgreSQL 寫入。")

            # 11. 更新前端網頁資料 (必做，因為 GitHub Pages 需要它)
            try:
                from update_web_data import export_to_web_data
                export_to_web_data(new_data=self.data)
            except Exception as e:
                logger.warning(f"更新前端資料失敗: {e}")
            
            # 統計資訊
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("=" * 60)
            logger.info("爬蟲執行完成！")
            logger.info(f"共抓取 {len(self.data)} 筆醫學中心資料")
            logger.info(f"執行時間: {duration:.2f} 秒")
            logger.info(f"CSV 檔案: {csv_file}")
            logger.info(f"JSON 檔案: {json_file}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"爬蟲執行失敗: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
        finally:
            # 關閉瀏覽器
            if self.driver:
                self.driver.quit()
                logger.info("已關閉瀏覽器")


def main():
    """主程式入口"""
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
