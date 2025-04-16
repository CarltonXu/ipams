import json

from flask import Blueprint, request, jsonify
from app.models import db, ScanSubnet, ScanPolicy, ScanJob
from app.utils.auth import token_required
from datetime import datetime
from app.tasks.scan import execute_scan_task

scan_executor_bp = Blueprint('scan', __name__)

# 执行扫描
@scan_executor_bp.route('/execute', methods=['POST'])
@token_required
def execute_scan(current_user):
    try:
        data = request.get_json()
        
        # 验证请求参数
        if not data or 'policy_id' not in data or 'subnet_ids' not in data:
            return jsonify({'error': '无效的请求参数'}), 400
            
        policy_id = data['policy_id']
        subnet_ids = data['subnet_ids']
        
        if not isinstance(subnet_ids, list):
            return jsonify({'error': '网段ID必须是一个列表'}), 400
        
        # 1. 验证策略是否存在且属于当前用户
        policy = ScanPolicy.query.filter_by(
            id=policy_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not policy:
            return jsonify({'error': '策略不存在或无权访问'}), 404
            
        # 2. 验证所选网段是否都存在且属于该策略
        policy_subnet_ids = json.loads(policy.subnet_ids) if policy.subnet_ids else []
        if not all(subnet_id in policy_subnet_ids for subnet_id in subnet_ids):
            return jsonify({'error': '选择的网段不属于该策略'}), 400
            
        subnets = ScanSubnet.query.filter(
            ScanSubnet.id.in_(subnet_ids),
            ScanSubnet.deleted == False
        ).all()
        
        if len(subnets) != len(subnet_ids):
            return jsonify({'error': '部分网段不存在'}), 400
            
        # 3. 检查是否有正在进行的扫描任务
        active_jobs = ScanJob.query.filter(
            ScanJob.user_id == current_user.id,
            ScanJob.status.in_(['pending', 'running']),
            ScanJob.policy_id == policy_id
        ).first()
        
        if active_jobs:
            return jsonify({'error': '该策略已有正在进行的扫描任务'}), 409
            
        # 4. 创建扫描任务
        jobs = []
        for subnet in subnets:
            job = ScanJob(
                user_id=current_user.id,
                policy_id=policy.id,
                subnet_id=subnet.id,
                status='pending',
                progress=0,
                start_time=datetime.utcnow(),
                machines_found=0
            )
            jobs.append(job)
            
        try:
            db.session.bulk_save_objects(jobs)
            db.session.commit()
            
            # 5. 异步执行扫描任务
            for job in jobs:
                execute_scan_task.delay(
                    job_id=job.id,
                    policy_id=policy.id,
                    subnet_id=job.subnet_id
                )

            return jsonify({
                'message': '扫描任务创建成功',
                'job_ids': [job.id for job in jobs]
            })
            
        except Exception as e:
            db.session.rollback()
            raise e
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500