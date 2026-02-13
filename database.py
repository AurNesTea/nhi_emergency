import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 資料庫連線設定
# 預設連線至 localhost，若在 Docker 環境中則透過環境變數覆寫為 'db'
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "nhi_emergency")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 建立資料庫引擎
engine = create_engine(DATABASE_URL)

# 建立 SessionLocal 類別
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 宣告對應的 Base 類別
Base = declarative_base()

def init_db():
    """初始化資料庫（建立資料表）"""
    # 重要：在此處匯入 models，確保 Base.metadata 包含所有模型定義
    # 如果未來有更多 models 檔案，都需要在這裡匯入
    import models
    
    try:
        Base.metadata.create_all(bind=engine)
        print(f"資料庫初始化成功，連線至: {DB_HOST}")
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")
        # 不中斷程式，僅記錄錯誤
        pass

def get_db():
    """取得資料庫連線 Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
