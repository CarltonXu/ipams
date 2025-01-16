from flask import Blueprint
from .subnet_routes import subnet_bp
from .policy_routes import policy_bp
from .job_routes import job_bp
from .scan import scan_executor_bp

scan_bp = Blueprint('scan', __name__)

scan_bp.register_blueprint(subnet_bp, url_prefix='/scan')
scan_bp.register_blueprint(policy_bp, url_prefix='/scan')
scan_bp.register_blueprint(job_bp, url_prefix='/scan')
scan_bp.register_blueprint(scan_executor_bp, url_prefix='/scan')