from flask import current_app
import smtplib
from email.mime.text import MIMEText

class EmailNotifier:
    def __init__(self, app=None):
        self.app = app

    def init_app(self, app):
        self.app = app

    def send(self, user_email, message, smtp_config=None):
        """Send email notification using SMTP"""
        try:
            msg = MIMEText(message)
            msg['Subject'] = 'IP Management System Notification'
            msg['From'] = smtp_config.get('from', 'noreply@example.com')
            msg['To'] = user_email
            
            with smtplib.SMTP(smtp_config.get('server', 'localhost')) as server:
                server.starttls()
                server.login(
                    smtp_config.get('username', ''),
                    smtp_config.get('password', '')
                )
                server.send_message(msg)
            return True
        except Exception as e:
            self.app.logger.error(f"Failed to send email notification: {str(e)}")
            raise