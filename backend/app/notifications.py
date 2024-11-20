from flask import current_app
import smtplib
from email.mime.text import MIMEText
import requests

def send_email_notification(user_email, message):
    """Send email notification using SMTP"""
    try:
        msg = MIMEText(message)
        msg['Subject'] = 'IP Management System Notification'
        msg['From'] = current_app.config['SMTP_FROM']
        msg['To'] = user_email
        
        with smtplib.SMTP(current_app.config['SMTP_SERVER']) as server:
            server.starttls()
            server.login(
                current_app.config['SMTP_USERNAME'],
                current_app.config['SMTP_PASSWORD']
            )
            server.send_message(msg)
            
    except Exception as e:
        current_app.logger.error(f"Failed to send email notification: {str(e)}")

def send_wechat_notification(wechat_id, message):
    """Send WeChat notification using WeChat Work API"""
    try:
        webhook_url = current_app.config['WECHAT_WEBHOOK_URL']
        payload = {
            'msgtype': 'text',
            'text': {
                'content': message
            }
        }
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
    except Exception as e:
        current_app.logger.error(f"Failed to send WeChat notification: {str(e)}")

def notify_user(user, message):
    """Send notification to user through available channels"""
    if user.email:
        send_email_notification(user.email, message)
    
    if user.wechat_id:
        send_wechat_notification(user.wechat_id, message)