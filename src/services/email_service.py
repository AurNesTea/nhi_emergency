import smtplib
import logging
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from src.config import EMAIL_CONFIG

logger = logging.getLogger(__name__)

def send_email(subject, body, attachment_path=None):
    """
    基礎郵件發送功能
    
    Args:
        subject (str): 郵件主旨
        body (str): 郵件內容
        attachment_path (str or Path, optional): 附件路徑
    """
    if not EMAIL_CONFIG['enabled']:
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = ", ".join(EMAIL_CONFIG['receiver_emails'])
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # 夾帶附件
        if attachment_path:
            file_path = Path(attachment_path)
            if file_path.exists():
                with open(file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=file_path.name)
                part['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
                msg.attach(part)
        
        # 發送郵件
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
            
        logger.info(f"Email 通知已發送至: {', '.join(EMAIL_CONFIG['receiver_emails'])}")
        
    except Exception as e:
        logger.error(f"發送 Email 時發生錯誤: {e}")

def send_scraping_report(data_count, attachment_path=None):
    """
    發送爬蟲執行結果報告
    
    Args:
        data_count (int): 抓取到的資料筆數
        attachment_path (str, optional): CSV 附件路徑
    """
    if not EMAIL_CONFIG['enabled']:
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    subject = f"{EMAIL_CONFIG['subject_prefix']} 醫學中心等待人數資料 ({timestamp})"
    
    body = f"""
    您好，
    
    這是自動發送的健保署醫學中心爬蟲報告。
    執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    抓取筆數：{data_count} 筆
    
    詳細資料請參考附件 CSV 檔案。
    """
    
    send_email(subject, body, attachment_path)
