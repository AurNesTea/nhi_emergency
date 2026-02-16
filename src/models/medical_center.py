from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from src.models.database import Base

class MedicalCenterRecord(Base):
    """
    醫學中心急診即時資料模型
    對應資料表: medical_center_records
    """
    __tablename__ = "medical_center_records"

    id = Column(Integer, primary_key=True, index=True)
    hospital_name = Column(String, index=True, comment="醫院簡稱")
    inpatient_waiting = Column(Integer, comment="住院等待人數")
    outpatient_waiting = Column(Integer, comment="看診等待人數")
    stretcher_waiting = Column(Integer, comment="推床等待人數")
    icu_waiting = Column(Integer, comment="加護病房等待人數")
    is_full_bed = Column(Boolean, default=False, comment="滿床通報(是/否)")
    created_at = Column(DateTime, default=datetime.now, comment="抓取時間")

    def __repr__(self):
        return f"<MedicalCenterRecord(hospital={self.hospital_name}, time={self.created_at})>"
