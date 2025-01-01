import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root123.@127.0.0.1:13306/ipams')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scanner configuration
    NETWORK_RANGE = os.getenv('NETWORK_RANGE', '192.168.0.0/20')
    SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 3600))  # Default: 1 hour
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_CAPTCHA_EXPIRE = int(os.getenv('REDIS_CAPTCHA_EXPIRE', 300))  # 5 minutes
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上传文件大小为16MB