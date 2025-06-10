from flask import current_app
from .email import EmailNotifier
from .wechat import WeChatNotifier
from app.models.models import SystemConfig
import time
from flask_sqlalchemy import SQLAlchemy

class NotificationManager:
    def __init__(self, app=None):
        self.app = app
        self.email_notifier = EmailNotifier(app)
        self.wechat_notifier = WeChatNotifier(app)
        self._config_cache = {}
        self._config_cache_time = 0
        self._config_cache_ttl = 300  # 配置缓存时间（秒）
        self.db = SQLAlchemy(app)

    def init_app(self, app):
        self.app = app
        self.email_notifier.init_app(app)
        self.wechat_notifier.init_app(app)
        # 初始化时加载配置
        self._load_configs()

    def _load_configs(self):
        """从数据库加载配置"""
        try:
            with self.app.app_context():
                configs = SystemConfig.query.all()
                self._config_cache = {config.key: config.value for config in configs}
                self._config_cache_time = time.time()
        except Exception as e:
            self.app.logger.error(f"Failed to load notification configs: {str(e)}")

    def _get_config(self, key, default=None):
        """获取配置值，支持缓存"""
        current_time = time.time()
        
        # 检查缓存是否过期
        if current_time - self._config_cache_time > self._config_cache_ttl:
            self._load_configs()
            
        return self._config_cache.get(key, default)

    def notify_user(self, user, message):
        """Send notification to user through available channels"""
        # 检查邮件通知是否启用
        if user.email and self._get_config('ENABLE_EMAIL_NOTIFICATION', 'true').lower() == 'true':
            smtp_config = {
                'server': self._get_config('SMTP_SERVER'),
                'username': self._get_config('SMTP_USERNAME'),
                'password': self._get_config('SMTP_PASSWORD'),
                'from': self._get_config('SMTP_FROM')
            }
            if all(smtp_config.values()):  # 确保所有SMTP配置都存在
                self.email_notifier.send(user.email, message)
        
        # 检查微信通知是否启用
        if user.wechat_id and self._get_config('ENABLE_WECHAT_NOTIFICATION', 'true').lower() == 'true':
            webhook_url = self._get_config('WECHAT_WEBHOOK_URL')
            if webhook_url:
                self.wechat_notifier.send(user.wechat_id, message)

    def update_config(self, key, value):
        """更新通知配置"""
        try:
            with self.app.app_context():
                config = SystemConfig.query.filter_by(key=key).first()
                if config:
                    config.value = value
                else:
                    config = SystemConfig(
                        key=key,
                        value=value,
                        description=f"Notification configuration for {key}",
                        is_public=False
                    )
                    self.db.session.add(config)
                
                self.db.session.commit()
                
                # 更新缓存
                self._config_cache[key] = value
                self._config_cache_time = time.time()
                
                return True
        except Exception as e:
            self.app.logger.error(f"Failed to update notification config: {str(e)}")
            return False

    def get_config(self, key, default=None):
        """获取通知配置"""
        return self._get_config(key, default)

    def get_all_configs(self):
        """获取所有通知配置"""
        return self._config_cache.copy() 