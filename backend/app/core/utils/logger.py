import logging
import os
from logging.handlers import RotatingFileHandler

# 创建应用日志记录器
app_logger = logging.getLogger('app')

def init_app(app):
    """初始化应用日志配置"""
    # 设置日志级别
    is_debug = app.config.get('DEBUG', False)
    log_level = logging.DEBUG if is_debug else logging.INFO
    app_logger.setLevel(log_level)
    
    # 清除现有的处理器
    for handler in app_logger.handlers[:]:
        app_logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)
    
    # 创建日志目录
    log_dir = app.config.get('LOG_PATH')
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except PermissionError as e:
        app_logger.warning(f'Failed to create logs directory: {e}')
    
    # 根据环境设置日志文件名
    log_filename = f"ipams.{'debug' if is_debug else 'prod'}.log"
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, log_filename),
        maxBytes=app.config.get('LOG_MAX_BYTES', 10*1024*1024),  # 默认10MB
        backupCount=app.config.get('LOG_BACKUP_COUNT', 5),
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # 添加文件处理器到logger
    app_logger.addHandler(file_handler)
    
    # 记录启动信息
    app_logger.debug(f"Logger initialized with level: {logging.getLevelName(log_level)}")
    app_logger.debug(f"Log file: {os.path.join(log_dir, log_filename)}") 