from flask import Blueprint
from app.routes.scan.subnet_routes import subnet_bp
from app.routes.scan.policy_routes import policy_bp
from app.routes.scan.job_routes import job_bp

scan_bp = Blueprint('scan', __name__)

scan_bp.register_blueprint(subnet_bp, url_prefix='/scan')
scan_bp.register_blueprint(policy_bp, url_prefix='/scan')
scan_bp.register_blueprint(job_bp, url_prefix='/scan')