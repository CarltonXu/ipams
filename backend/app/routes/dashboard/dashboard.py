from flask import Blueprint, jsonify
from app.utils.auth import token_required
from app.models import IP, ScanPolicy, ScanJob, ActionLog
from app.utils.utils import get_system_metrics
from app.tasks.task_manager import task_manager

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_data(current_user):
    total_ips = IP.query.count()
    claimed_ips = IP.query.filter_by(status='active').count()
    unclaimed_ips = total_ips - claimed_ips
    user_claimed_ips = IP.query.filter_by(status='active', assigned_user_id=current_user.id).count()

    total_policies = ScanPolicy.query.count()
    running_jobs = ScanJob.query.filter_by(status='running').count()
    failed_jobs = ScanJob.query.filter_by(status='failed').count()
    successful_jobs = ScanJob.query.filter_by(status='completed').count()

    # 获取最近的扫描任务
    recent_jobs = ScanJob.query.order_by(ScanJob.created_at.desc()).limit(10).all()
    recent_jobs_data = []
    for job in recent_jobs:
        job_data = job.to_dict()
        # 获取任务管理器中的状态
        task_status = task_manager.get_task_status(job.id)
        job_data['task_status'] = task_status
        recent_jobs_data.append(job_data)

    audit_resources = ActionLog.query.all()

    system_metrics = get_system_metrics()

    return jsonify({
        'stats': {
            'total_ips': total_ips,
            'claimed_ips': claimed_ips,
            'unclaimed_ips': unclaimed_ips,
            'user_claimed_ips': user_claimed_ips,
            'total_policies': total_policies,
            'running_jobs': running_jobs,
            'failed_jobs': failed_jobs,
            'successful_jobs': successful_jobs,
            'cpu_usage': system_metrics['cpu_usage'],
            'memory_usage': system_metrics['memory_usage'],
            'disk_usage': system_metrics['disk_usage'],
        },
        'resources': {
            'audit_resources': [resource.to_dict() for resource in audit_resources]
        },
        'recent_jobs': recent_jobs_data
    })