from flask import Blueprint, request, jsonify
from app.models import db, ScanJob, ScanSubnet, ScanResult
from app.utils.auth import token_required
from datetime import datetime
from app.tasks.task_manager import task_manager

job_bp = Blueprint('job', __name__)

@job_bp.route('/jobs', methods=['GET'])
@token_required
def get_jobs(current_user):
    """Get all scan jobs for current user"""
    jobs = ScanJob.query.filter_by(user_id=current_user.id).all()
    return jsonify([job.to_dict() for job in jobs])

@job_bp.route('/jobs', methods=['POST'])
@token_required
def create_job(current_user):
    """Create new scan job"""
    data = request.json
    subnet_ids = data.get('subnet_ids', [])
    policy_id = data.get('policy_id')
    
    if not policy_id or not subnet_ids:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        # 验证所有网段是否存在且属于当前用户
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
            # Create new job record
            new_job = ScanJob(
                user_id=current_user.id,
                subnet_id=subnet.id,
                policy_id=policy_id,
                status='pending',
                progress=0,
                start_time=datetime.utcnow(),
                machines_found=0
            )
            
            db.session.add(new_job)
            db.session.commit()  # 先提交事务，确保job记录存在
            
            try:
                # Submit task to task manager
                task_manager.submit_scan_task(new_job.id, policy_id, subnet.id)
                jobs.append(new_job)
            except Exception as e:
                # 如果任务提交失败，更新job状态
                new_job.status = 'failed'
                new_job.error_message = str(e)
                new_job.end_time = datetime.utcnow()
                db.session.commit()
                raise
        
        return jsonify({
            'message': 'Scan jobs created successfully',
            'jobs': [job.to_dict() for job in jobs]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/jobs/<job_id>', methods=['GET'])
@token_required
def get_job_status(current_user, job_id):
    """Get scan job status"""
    try:
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
        
        return jsonify({
            'job_id': job_id,
            'status': task_status,
            'job': {
                'id': job.id,
                'status': job.status,
                'progress': job.progress,
                'machines_found': job.machines_found,
                'start_time': job.start_time.isoformat() if job.start_time else None,
                'end_time': job.end_time.isoformat() if job.end_time else None,
                'error_message': job.error_message
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
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
        return jsonify({'error': 'Job cannot be cancelled'}), 400
    
    try:
        # Update job status
        job.status = 'cancelled'
        job.end_time = datetime.utcnow()
        db.session.commit()
        
        # Update task status in task manager
        task_state = task_manager.get_task_status(job_id)
        if task_state['status'] != 'not_found':
            task_manager.update_task_status(job_id, 'cancelled')
        
        return jsonify({'message': 'Job cancelled successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/jobs/<job_id>/results', methods=['GET'])
@token_required
def get_job_results(current_user, job_id):
    """Get scan results for a specific job"""
    job = ScanJob.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first()
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    results = ScanResult.query.filter_by(job_id=job_id).all()
    return jsonify([result.to_dict() for result in results])