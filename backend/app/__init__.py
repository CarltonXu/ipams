import atexit
import os
import time

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from redis import Redis
from sqlalchemy import text

from app.core.config.settings import Config
from app.models.models import db
from app.api.v1 import v1_bp
from app.tasks.task_manager import task_manager
from app.services.scan.scheduler import PolicyScheduler
from app.core.middleware import register_error_handlers
from app.core.error.errors import DatabaseError
from app.services.notification import NotificationManager
from app.scripts.init_notification_templates import init_notification_templates
from app.tasks.system_metrics import metrics_scheduler
from app.core.utils.logger import app_logger as logger, init_app as init_logger
from app.services.collection.collector_manager import collector_manager
from app.services.export.excel_exporter import excel_exporter

# 创建 db 实例
migrate = Migrate()

scheduler = PolicyScheduler()

# 创建通知管理器实例
notification_manager = NotificationManager()

def create_redis_client(app):
    """创建Redis客户端连接"""
    max_retries = 3
    retry_delay = 2  # 秒
    
    for attempt in range(max_retries):
        try:
            client = Redis(
                host=app.config['REDIS_HOST'],
                port=app.config['REDIS_PORT'],
                password=app.config['REDIS_PASSWORD'],
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # 测试连接
            client.ping()
            logger.debug("Redis connection established successfully")
            return client
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {str(e)}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Redis connection failed after {max_retries} attempts: {str(e)}")
                raise DatabaseError(
                    message="无法连接到 Redis 服务器",
                    details={'original_error': str(e)}
                )

def init_extensions(app):
    """初始化扩展"""
    try:
        # 初始化日志
        init_logger(app)
        logger.debug("Logger initialized successfully")

        # 初始化数据库
        db.init_app(app)
        migrate.init_app(app, db)
        
        # 测试数据库连接（添加重试逻辑）
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                with app.app_context():
                    db.session.execute(text('SELECT 1'))
                    logger.debug("Database connection established successfully")
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(retry_delay)
                else:
                    error_msg = str(e)
                    if "timed out" in error_msg:
                        error_msg = "数据库连接超时"
                    elif "Can't connect" in error_msg:
                        error_msg = "无法连接到数据库服务器"
                    logger.error(f"Database connect failed: {error_msg}")
                    raise DatabaseError(
                        message=error_msg,
                        details={'server': app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1].split('/')[0]}
                    )
        
        # 初始化Redis
        redis_client = create_redis_client(app)
        app.extensions['redis'] = redis_client
        
        # 初始化任务管理器
        task_manager.init_app(app)
        logger.debug("Task manager initialized successfully")
        
        # 初始化调度器
        scheduler.init_app(app)
        logger.debug("Scheduler initialized successfully")

        # 初始化系统监控调度器
        metrics_scheduler.init_app(app)
        logger.debug('Monitor scheduler initialized successfully')
        
        # 初始化通知管理器
        notification_manager.init_app(app)
        app.notification_manager = notification_manager
        logger.debug("Notification manager initialized successfully")
        
        # 初始化采集管理器
        collector_manager.init_app(app)
        logger.debug("Collector manager initialized successfully")
        
        # 初始化Excel导出器
        excel_exporter.init_app(app)
        logger.debug("Excel exporter initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {str(e)}")
        raise

def create_app(config_object=None):
    app = Flask(__name__)
    
    # 加载配置
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)

    # 初始化CORS，允许所有域名访问
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册蓝图
    app.register_blueprint(v1_bp)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        try:
            # 确保上传目录存在
            upload_folder = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # 记录请求信息
            logger.debug(f"Attempting to access file: {filename}")
            logger.debug(f"Upload folder: {upload_folder}")
            
            # 检查文件是否存在
            file_path = os.path.join(upload_folder, filename)
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return "File not found", 404
                
            return send_from_directory(upload_folder, filename)
        except Exception as e:
            logger.error(f"Error serving file {filename}: {str(e)}")
            return str(e), 500
    
    # 初始化扩展
    init_extensions(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        logger.debug("Database tables created successfully")
        
        # 初始化通知模板
        init_notification_templates()
        logger.debug("Notification templates initialized successfully")
    

    
    return app

def get_app():
    """获取应用实例，用于Flask CLI"""
    from app.core.config.settings import get_config
    return create_app(get_config())