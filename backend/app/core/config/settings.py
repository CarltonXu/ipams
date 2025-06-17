import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:root123.@127.0.0.1:13306/ipams')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour

    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_CAPTCHA_EXPIRE = int(os.getenv('REDIS_CAPTCHA_EXPIRE', 300))  # 5 minutes

    # 文件上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_PATH', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上传文件大小为16MB

    # 设置日志配置
    LOG_MAX_BYTES =int(os.getenv('LOG_MAX_BYTES', 10*1024*1024))
    LOG_BACKUP_COUNT= int(os.getenv('LOG_BACKUP_COUNT', 5))
    LOG_PATH = os.getenv('LOG_PATH', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'logs'))

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = str(os.getenv('DEBUG', 'False')).lower() == 'true'
    TESTING = False

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'mysql+pymysql://root:password@127.0.0.1/ipams_test')

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = str(os.getenv('DEBUG', 'False')).lower() == 'true'
    TESTING = False

    # 生产环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 获取当前配置
def get_config():
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])