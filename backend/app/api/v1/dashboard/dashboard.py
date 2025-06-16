from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from app.core.security.auth import token_required
from app.models.models import IP, ScanPolicy, ScanJob, ActionLog
from app.core.utils.helpers import get_system_info

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_data(current_user):
    try:
        # 获取IP统计
        total_ips = IP.query.count()
        claimed_ips = IP.query.filter_by(status='active').count()
        unclaimed_ips = total_ips - claimed_ips
        # 获取策略统计
        total_policies = ScanPolicy.query.count()
        
        # 获取任务统计
        running_jobs = ScanJob.query.filter_by(status='running').count()
        failed_jobs = ScanJob.query.filter_by(status='failed').count()
        successful_jobs = ScanJob.query.filter_by(status='completed').count()
        
        # 获取最近的审计日志
        recent_audits = ActionLog.query.order_by(ActionLog.created_at.desc()).limit(10).all()
        
        # 获取最近的任务
        recent_jobs = ScanJob.query.order_by(ScanJob.created_at.desc()).limit(10).all()
        
        # 获取系统信息
        system_info = get_system_info()
        
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': {
                'stats': {
                    'total_ips': total_ips,
                    'claimed_ips': claimed_ips,
                    'unclaimed_ips': unclaimed_ips,
                    'total_policies': total_policies,
                    'running_jobs': running_jobs,
                    'failed_jobs': failed_jobs,
                    'successful_jobs': successful_jobs,
                },
                'resources': {
                    'audit_resources': [audit.to_dict() for audit in recent_audits],
                    'system_info': system_info
                },
                'recent_jobs': [job.to_dict() for job in recent_jobs]
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'Failed to get dashboard data: {str(e)}'
        }), 500