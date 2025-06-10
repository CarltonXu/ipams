from flask import Blueprint
from .scan import scan_bp
from .auth import auth_bp
from .user import user_bp
from .dashboard import dashboard_bp
from .ip import ips_bp
from .subnet import subnet_bp
from .policy import policy_bp
from .task import task_bp
from .config import config_bp

# 主蓝图，使用 /v1 前缀
v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

# 注册子蓝图
v1_bp.register_blueprint(scan_bp)
v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(user_bp)
v1_bp.register_blueprint(dashboard_bp)
v1_bp.register_blueprint(ips_bp)
v1_bp.register_blueprint(subnet_bp)
v1_bp.register_blueprint(policy_bp)
v1_bp.register_blueprint(task_bp)
v1_bp.register_blueprint(config_bp)

__all__ = ['v1_bp']
