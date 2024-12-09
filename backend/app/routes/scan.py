from flask import Blueprint, request, jsonify
from backend.app.models import db, ScanSubnet, ScanPolicy, ScanJob
from backend.app.utils.auth import token_required, admin_required
from datetime import datetime

scan_bp = Blueprint('scan', __name__)

# 校验网段格式的工具
import ipaddress

def validate_subnet(subnet):
    try:
        ipaddress.IPv4Network(subnet)
        return True
    except ValueError:
        return False

# 获取所有扫描网段
@scan_bp.route('/subnets', methods=['GET'])
@token_required
def get_subnets(current_user):
    subnets = ScanSubnet.query.filter_by(user_id=current_user.id, deleted=False).all()
    return jsonify([{
        'id': subnet.id,
        'subnet': subnet.subnet,
        'created_at': subnet.created_at,
        'updated_at': subnet.updated_at
    } for subnet in subnets])

# 添加扫描网段
@scan_bp.route('/subnets', methods=['POST'])
@token_required
def add_subnet(current_user):
    data = request.json
    subnet = data.get('subnet')

    if not validate_subnet(subnet):
        return jsonify({'error': 'Invalid subnet format'}), 400

    new_subnet = ScanSubnet(user_id=current_user.id, subnet=subnet)
    db.session.add(new_subnet)
    db.session.commit()
    return jsonify({'message': 'Subnet added successfully', 'id': new_subnet.id}), 201

# 配置扫描策略
@scan_bp.route('/policies', methods=['POST'])
@token_required
def add_policy(current_user):
    data = request.json
    subnet_id = data.get('subnet_id')
    schedule = data.get('schedule')
    threads = data.get('threads', 1)

    if schedule not in ['hourly', 'daily', 'weekly', 'monthly', 'yearly']:
        return jsonify({'error': 'Invalid schedule'}), 400

    policy = ScanPolicy(user_id=current_user.id, subnet_id=subnet_id, schedule=schedule, threads=threads)
    db.session.add(policy)
    db.session.commit()
    return jsonify({'message': 'Policy created successfully', 'id': policy.id}), 201

# 查询扫描任务进度
@scan_bp.route('/jobs/<job_id>', methods=['GET'])
@token_required
def get_job_progress(job_id):
    job = ScanJob.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'id': job.id,
        'status': job.status,
        'progress': job.progress,
        'start_time': job.start_time,
        'end_time': job.end_time,
        'machines_found': job.machines_found
    })