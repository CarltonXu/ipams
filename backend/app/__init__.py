from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from .models import db
from .routes.user import api_bp
from .routes.scan import scan_bp
from .scanner import setup_scanner

# 创建 db 实例
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化数据库
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize extensions
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(scan_bp, url_prefix="/api/scan")

    # Setup scanner
    #setup_scanner(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app