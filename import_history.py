import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 取得目前檔案所在的目錄 (不論是在根目錄還是 utils)
BASE_DIR = Path(__file__).resolve().parent
if (BASE_DIR / "data").exists():
    ROOT_DIR = BASE_DIR
else:
    ROOT_DIR = BASE_DIR.parent

# 將根目錄加入路徑以便匯入
sys.path.append(str(ROOT_DIR))

from database import SessionLocal, init_db
from models import MedicalCenterRecord

def parse_int(value):
    """處理可能的非數字字符，例如 '-'"""
    if str(value).strip() == "-":
        return 0
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return 0

def import_history_from_json(json_path):
    """從 JSON 檔案匯入歷史資料到資料庫"""
    if not Path(json_path).exists():
        print(f"錯誤：找不到檔案 {json_path}")
        # 額外檢查嘗試路徑
        print(f"目前嘗試路徑為: {os.path.abspath(json_path)}")
        return

    print(f"正在讀取檔案：{json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"找到 {len(data)} 筆資料，準備寫入資料庫...")
    
    # 初始化資料庫 (確保資料表已建立)
    init_db()
    
    db = SessionLocal()
    success_count = 0
    error_count = 0

    try:
        for i, item in enumerate(data):
            try:
                # 轉換滿床通報狀態
                is_full_bed = True if "是" in item.get('滿床通報狀態', '') else False
                
                # 建立模型實例
                record = MedicalCenterRecord(
                    hospital_name=item.get('醫院簡稱'),
                    inpatient_waiting=parse_int(item.get('住院等待人數')),
                    outpatient_waiting=parse_int(item.get('看診等待人數')),
                    stretcher_waiting=parse_int(item.get('推床等待人數')),
                    icu_waiting=parse_int(item.get('加護病房等待人數')),
                    is_full_bed=is_full_bed,
                    created_at=datetime.strptime(item.get('抓取時間'), '%Y-%m-%d %H:%M:%S')
                )
                db.add(record)
                success_count += 1
                
                # 每 100 筆 commit 一次
                if success_count % 100 == 0:
                    db.commit()
                    print(f"進度：已處理 {success_count} 筆...")
            except Exception as e:
                print(f"跳過第 {i+1} 筆資料 (醫院: {item.get('醫院簡稱')}): {e}")
                error_count += 1
        
        # 最後的 commit
        db.commit()
        print(f"\n匯入完成！")
        print(f"成功：{success_count} 筆")
        print(f"失敗：{error_count} 筆")

    except Exception as e:
        print(f"發生嚴重錯誤：{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # 根據 ROOT_DIR 定位 data 資料夾
    history_json = ROOT_DIR / "data" / "medical_centers_history.json"
    import_history_from_json(history_json)
