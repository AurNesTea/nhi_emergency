import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import EMAIL_CONFIG
import sys

def test_email_connection():
    print("="*60)
    print("Email 通知設定測試工具")
    print("="*60)
    
    # Check if enabled
    if not EMAIL_CONFIG.get('enabled'):
        print("[!] 警告: config.py 中的 'enabled' 設定為 False")
        print("    請先將其改為 True 才能啟用通知功能。")
        # We proceed anyway for testing purposes
    
    print(f"[*] SMTP 伺服器: {EMAIL_CONFIG.get('smtp_server')}")
    print(f"[*] SMTP 連接埠: {EMAIL_CONFIG.get('smtp_port')}")
    print(f"[*] 寄件者: {EMAIL_CONFIG.get('sender_email')}")
    print(f"[*] 收件者: {EMAIL_CONFIG.get('receiver_emails')}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = ", ".join(EMAIL_CONFIG['receiver_emails'])
        msg['Subject'] = f"[測試] 健保署爬蟲通知系統測試 ({datetime.now().strftime('%H:%M:%S')})"
        
        body = f"""
        您好，
        
        這是一封測試郵件，用以確認健保署爬蟲的 Email 通知設定是否正確。
        
        如果您收到這封信，代表 SMTP 設定與應用程式密碼均已正確設定。
        
        測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        print("\n正在嘗試連線至 SMTP 伺服器...")
        
        # Connect
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        print("正在嘗試登入...")
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        
        print("正在發送測試郵件...")
        server.send_message(msg)
        server.quit()
        
        print("\n[+] 成功！測試郵件已發送。")
        print("    請檢查您的收件匣 (包含垃圾郵件匣)。")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n[!] 錯誤：認證失敗")
        print("    可能原因：")
        print("    1. Email 帳號或應用程式密碼錯誤")
        print("    2. 如果使用 Gmail，請確認已使用「應用程式密碼」而非登入密碼")
        print("    3. 兩步驟驗證未開啟 (Gmail 必須開啟才能使用應用程式密碼)")
    except Exception as e:
        print(f"\n[!] 發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        
    return False

if __name__ == "__main__":
    test_email_connection()
