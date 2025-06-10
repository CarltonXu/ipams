import requests

class WeChatNotifier:
    def __init__(self, app=None):
        self.app = app

    def init_app(self, app):
        self.app = app

    def send(self, wechat_id, message, webhook_url=None):
        """Send WeChat notification using WeChat Work API"""
        try:
            if not webhook_url:
                self.app.logger.error("Webhook URL not provided")
                return
                
            payload = {
                'msgtype': 'text',
                'text': {
                    'content': message
                }
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
        except Exception as e:
            self.app.logger.error(f"Failed to send WeChat notification: {str(e)}") 