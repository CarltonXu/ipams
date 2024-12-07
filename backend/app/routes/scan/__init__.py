from flask import Blueprint
from .subnet_routes import subnet_bp
from .policy_routes import policy_bp
from .job_routes import job_bp

scan_bp = Blueprint('scan', __name__, url_prefix='/scan')

# Register sub-blueprints
scan_bp.register_blueprint(subnet_bp, url_prefix='/subnets')
scan_bp.register_blueprint(policy_bp, url_prefix='/policies')
scan_bp.register_blueprint(job_bp, url_prefix='/jobs')