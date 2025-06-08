import atexit
import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from redis import Redis

from app.config import Config
from app.models.models import db
from app.routes.scan import scan_bp
from app.routes.user.user import user_bp
from app.routes.auth.auth import auth_bp
from app.routes.ip.ips import ips_bp
from app.routes.dashboard.dashboard import dashboard_bp
from app.tasks.task_manager import task_manager
from app.scheduler import scheduler

# 创建 db 实例
migrate = Migrate()

def create_redis_client(app):
    """创建Redis客户端连接"""
    try:
        client = Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            password=app.config['REDIS_PASSWORD'],
            decode_responses=True,
            socket_timeout=2,  # 添加超时设置
            socket_connect_timeout=2,
            retry_on_timeout=True,  # 超时重试
            health_check_interval=30  # 定期健康检查
        )
        # 测试连接
        client.ping()
        return client
    except Exception as e:
        app.logger.error(f"Redis connection failed: {str(e)}")
        raise

def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    # 初始化数据库
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 初始化Redis
    try:
        redis_client = create_redis_client(app)
        app.extensions['redis'] = redis_client
        app.logger.info("Redis connection established successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize Redis: {str(e)}")
        # 这里可以决定是否要继续运行应用
        # 如果Redis是必需的，可以raise异常终止应用启动
        # raise e
    
    # Initialize extensions
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(scan_bp, url_prefix="/api")
    app.register_blueprint(ips_bp, url_prefix="/api")

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # 初始化调度器
        scheduler.init_app(app)
        
        # 初始化任务管理器
        task_manager.init_app(app)
    
    # 在应用退出时关闭任务管理器
    atexit.register(task_manager.shutdown)
    return app