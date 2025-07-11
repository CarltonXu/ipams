import json

from flask import Blueprint, request, jsonify
from app.models.models import db, ScanJob, ScanPolicy, ScanSubnet, ScanResult
from app.core.security.auth import token_required
from app.tasks.task_manager import task_manager
from datetime import datetime

task_bp = Blueprint('task', __name__)

@task_bp.route('/task', methods=['GET'])
@token_required
def get_jobs(current_user):
    """Get all scan jobs for current user"""
    try:
        # 获取查询参数
        status = request.args.getlist('status')  # 支持多个状态
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        # 构建基础查询
        query = ScanJob.query.filter_by(
            user_id=current_user.id,
            deleted=False
        )
        
        # 如果指定了状态，添加状态过滤
        if status:
            query = query.filter(ScanJob.status.in_(status))
        
        # 计算总数
        total = query.count()
        
        # 添加分页
        jobs = query.order_by(ScanJob.start_time.desc()) \
                   .offset((page - 1) * page_size) \
                   .limit(page_size) \
                   .all()
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs],
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/task', methods=['POST'])
@token_required
def create_job(current_user):
    """Create new scan task"""
    try: 
        data = request.json
        subnet_ids = data.get('subnet_ids', [])
        policy_id = data.get('policy_id')
    
        if not policy_id or not subnet_ids:
            return jsonify({'error': 'Missing required parameters'}), 400

        # 获取策略信息
        policy = ScanPolicy.query.filter_by(
            id=policy_id,
            user_id=current_user.id,
            deleted=False
        ).first()

        if not policy:
            return jsonify({'error': 'Scan policy is not exists.'}), 400

        # 解析策略中的扫描计划
        strategies = json.loads(policy.strategies) if isinstance(policy.strategies, str) else policy.strategies

        # 验证所有的子网是否都存在
        subnets = []
        for subnet_id in subnet_ids:
            subnet = ScanSubnet.query.filter_by(
                id=subnet_id,
                user_id=current_user.id,
                deleted=False
            ).first()
    
            if not subnet:
                return jsonify({'error': f'Invalid subnet: {subnet_id}'}), 400
            subnets.append(subnet)

        # 为每个网段创建扫描任务
        jobs = []
        for subnet in subnets:
            # 查找包含当前子网的策略
            matching_strategy = None
            for strategy in strategies:
                if subnet_id in strategy.get('subnet_ids', []):
                    matching_strategy = strategy
                    break        

            if not matching_strategy:
                continue

            # 获取扫描参数
            scan_params = matching_strategy.get('scan_params', {
                'enable_custom_ports': False,
                'ports': '',
                'enable_custom_scan_type': False,
                'scan_type': 'default'
            })

            try:
                # Submit task to task manager
                job = task_manager.submit_scan_task(None, policy_id, subnet.id, scan_params)
                jobs.append(job)
            except Exception as e:
                raise f"Submit scan task failed, error: {e}"
            
        return jsonify({
            'message': 'Scan jobs created successfully',
            'jobs': [job.to_dict() for job in jobs]
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@task_bp.route('/task/<job_id>', methods=['GET'])
@token_required
def get_job_status(current_user, job_id):
    """Get scan job status"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        # 验证任务是否存在且属于当前用户
        job = ScanJob.query.filter_by(
            id=job_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not job:
            return jsonify({'error': 'Job not found or unauthorized'}), 404
        
        # 获取任务状态
        task_status = task_manager.get_task_status(job_id)
        
        # 只返回可序列化的数据
        serializable_status = {
            'status': task_status.get('status'),
            'progress': task_status.get('progress'),
            'machines_found': task_status.get('machines_found'),
            'error': task_status.get('error')
        }
        
        # 获取扫描结果并分页
        results_query = ScanResult.query.filter_by(job_id=job_id)
        total = results_query.count()
        results = results_query.order_by(ScanResult.created_at.desc()) \
                             .offset((page - 1) * page_size) \
                             .limit(page_size) \
                             .all()
        
        return jsonify({
            'job_id': job_id,
            'status': serializable_status,
            'job': job.to_dict(),
            'results': [result.to_dict() for result in results],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/task/<job_id>/cancel', methods=['POST'])
@token_required
def cancel_job(current_user, job_id):
    """Cancel running scan job"""
    job = ScanJob.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first()
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    if job.status not in ['pending', 'running']:
        return jsonify({'error': 'Only pending or running jobs can be cancelled'}), 400
    
    try:
        # Update job status
        job.status = 'cancelled'
        job.end_time = datetime.utcnow()
        db.session.commit()
        
        # cancel task job.
        task_manager.cancel_task(job_id)
        
        return jsonify({'message': 'Job cancelled successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@task_bp.route('/task/<job_id>/results', methods=['GET'])
@token_required
def get_job_results(current_user, job_id):
    """Get scan results for a specific job"""
    job = ScanJob.query.filter_by(id=job_id).first()
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    # 检查权限：只有管理员或任务所有者可以访问
    if not current_user.is_admin and job.user_id != current_user.id:
        return jsonify({'error': 'Permission denied: Only administrators or job owners can access these results'}), 403
        
    results = ScanResult.query.filter_by(job_id=job_id).all()
    return jsonify([result.to_dict() for result in results])