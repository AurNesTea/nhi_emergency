import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 將專案目錄加入路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def export_to_web_data(limit=100, new_data=None):
    """
    更新前端所需的 data.js 格式
    - 如果有資料庫，優先從資料庫撈取 (本地/Docker 調試)
    - 如果沒有資料庫 (GitHub Actions)，從現有的 data.js 讀取並追加最新結果
    """
    output_path = Path(__file__).parent / "data.js"
    
    # 嘗試從資料庫讀取
    try:
        from database import SessionLocal
        from models import MedicalCenterRecord
        db = SessionLocal()
        all_records = db.query(MedicalCenterRecord).order_by(MedicalCenterRecord.created_at.asc()).all()
        
        if all_records:
            grouped_data = {}
            for r in all_records:
                time_str = r.created_at.strftime('%Y-%m-%d %H:%M:%S')
                if time_str not in grouped_data:
                    grouped_data[time_str] = []
                
                grouped_data[time_str].append({
                    "hospital_name": r.hospital_name,
                    "inpatient_waiting": r.inpatient_waiting,
                    "outpatient_waiting": r.outpatient_waiting,
                    "stretcher_waiting": r.stretcher_waiting,
                    "icu_waiting": r.icu_waiting,
                    "is_full_bed": r.is_full_bed
                })
            
            final_list = [{"date": ts, "records": rs} for ts, rs in grouped_data.items()]
            final_list = final_list[-limit:]
            
            # 寫入檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"const scraperData = {json.dumps(final_list, ensure_ascii=False, indent=2)};")
            print(f"從資料庫匯出成功：{output_path}")
            return
    except Exception:
        print("無法從資料庫讀取，嘗試檔案追加模式 (針對 GitHub Actions)")

    # 檔案追加模式 (適用於無資料庫環境)
    current_data = []
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 簡單的地取出一對 JSON 字串
                json_str = content.replace("const scraperData =", "").strip().rstrip(';')
                current_data = json.loads(json_str)
        except Exception as e:
            print(f"讀取現有 data.js 失敗: {e}")

    # 加入新抓取的資料
    if new_data:
        # 確保格式正確 (來自 scraper 的 raw data)
        new_entry = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "records": [{
                "hospital_name": r.get('醫院簡稱'),
                "inpatient_waiting": r.get('住院等待人數'),
                "outpatient_waiting": r.get('看診等待人數'),
                "stretcher_waiting": r.get('推床等待人數'),
                "icu_waiting": r.get('加護病房等待人數'),
                "is_full_bed": ("是" in r.get('滿床通報狀態', ''))
            } for r in new_data]
        }
        current_data.append(new_entry)
        current_data = current_data[-limit:]  # 保留最近的
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"const scraperData = {json.dumps(current_data, ensure_ascii=False, indent=2)};")
        print(f"檔案追加模式成功：{output_path}")

if __name__ == "__main__":
    # 單獨執行時不做任何事或讀取最近一個 json
    export_to_web_data()
