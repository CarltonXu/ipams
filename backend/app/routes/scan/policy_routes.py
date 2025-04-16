from flask import Blueprint, request, jsonify
from app.models import db, ScanPolicy, ScanSubnet, ScanJob
from app.utils.auth import token_required
from sqlalchemy.exc import IntegrityError
import dateutil.parser
import json

policy_bp = Blueprint('policy', __name__)

@policy_bp.route('/policies', methods=['GET'])
@token_required
def get_policies(current_user):
    """Get all scan policies with their associated subnets"""
    try:
        policies = ScanPolicy.query.filter_by(
            user_id=current_user.id,
            deleted=False
        ).all()
        
        result = []
        for policy in policies:
            try:
                subnet_ids = policy.subnet_ids if policy.subnet_ids else []
                
                subnets = []
                if subnet_ids:
                    subnet_id_list = json.loads(subnet_ids)
                    subnets = ScanSubnet.query.filter(
                        ScanSubnet.id.in_(subnet_id_list),
                        ScanSubnet.deleted == False
                    ).all()
                
                policy_data = {
                    "id": policy.id,
                    "name": policy.name,
                    "description": policy.description,
                    "strategies": policy.strategies,
                    "start_time": policy.start_time,
                    "threads": policy.threads,
                    "status": policy.status,
                    "created_at": policy.created_at.isoformat() if policy.created_at else None,
                    "subnets": [
                        {
                            "id": subnet.id,
                            "name": subnet.name,
                            "subnet": subnet.subnet
                        } for subnet in subnets
                    ]
                }
                result.append(policy_data)
            except json.JSONDecodeError:
                print(f"Error decoding subnet_ids for policy {policy.id}: {policy.subnet_ids}")
                continue
            except Exception as e:
                print(f"Error processing policy {policy.id}: {str(e)}")
                continue
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in get_policies: {str(e)}")
        return jsonify({'error': str(e)}), 500


# 保存扫描策略配置
@policy_bp.route('/policies', methods=['POST'])
@token_required
def save_policy_config(current_user):
    """Save complete scan policy configuration"""
    data = request.json
    print("Received data:", data)
    
    try:
        existing_subnets = {
            subnet.subnet: subnet 
            for subnet in ScanSubnet.query.filter_by(
                user_id=current_user.id,
                deleted=False
            ).all()
        }
        
        existing_policies = {
            policy.name: policy 
            for policy in ScanPolicy.query.filter_by(
                user_id=current_user.id,
                deleted=False
            ).all()
        }
        
        subnet_map = {}
        for subnet_data in data.get('subnets', []):
            subnet_key = subnet_data['subnet']
            
            if subnet_key in existing_subnets:
                subnet = existing_subnets[subnet_key]
                subnet.name = subnet_data['name']
            else:
                subnet = ScanSubnet(
                    name=subnet_data['name'],
                    subnet=subnet_data['subnet'],
                    user_id=current_user.id
                )
                db.session.add(subnet)
            
            db.session.flush()
            subnet_map[subnet_data['name']] = subnet.id
        
        print("Subnet map:", subnet_map) 
        
        for policy_data in data.get('policies', []):
            policy_name = policy_data['name']
            subnet_names = []
            for subnet in data.get('subnets', []):
                subnet_names.append(subnet['name'])
            
            print(f"Processing policy {policy_name} with subnets: {subnet_names}")  # 调试日志
            
            subnet_id_list = [str(subnet_map[name]) for name in subnet_names if name in subnet_map]
            
            if policy_name in existing_policies:
                policy = existing_policies[policy_name]
                policy.description = policy_data['description']
                policy.strategies = policy_data['cron']
                policy.start_time = dateutil.parser.parse(policy_data['startTime'])
                policy.subnet_ids = subnet_id_list
            else:
                policy = ScanPolicy(
                    name=policy_name,
                    description=policy_data['description'],
                    strategies=policy_data['cron'],
                    user_id=current_user.id,
                    subnet_ids=subnet_id_list,
                    start_time=dateutil.parser.parse(policy_data['startTime']),
                )
                db.session.add(policy)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Configuration saved successfully',
            'subnet_map': subnet_map,
            'subnet_names': subnet_names
        })
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': str(ve)}), 400
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({'error': 'Duplicate subnet or policy name'}), 400
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

# 更新扫描策略
@policy_bp.route('/policies/<policy_id>', methods=['PUT'])
@token_required
def update_policy(current_user, policy_id):
    """Update existing policy"""
    policy = ScanPolicy.query.filter_by(
        id=policy_id,
        user_id=current_user.id
    ).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    data = request.json
    
    if 'subnet_id' in data:
        subnet = ScanSubnet.query.filter_by(
            id=data['subnet_id'],
            user_id=current_user.id,
            deleted=False
        ).first()
        if not subnet:
            return jsonify({'error': 'Invalid subnet'}), 400
        policy.subnet_id = data['subnet_id']
    
    policy.name = data.get('name', policy.name)
    policy.strategies = data.get('strategies', policy.strategies)
    policy.threads = data.get('threads', policy.threads)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Policy updated successfully',
        'policy': policy.to_dict()
    })

# 删除扫描策略
@policy_bp.route('/policies/<policy_id>', methods=['DELETE'])
@token_required
def delete_policy(current_user, policy_id):
    """Delete policy"""
    policy = ScanPolicy.query.filter_by(
        id=policy_id,
        user_id=current_user.id
    ).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    db.session.delete(policy)
    db.session.commit()
    
    return jsonify({'message': 'Policy deleted successfully'})

# 获取扫描策略的任务
@policy_bp.route('/policies/<policy_id>/jobs', methods=['GET'])
@token_required
def get_policy_jobs(current_user, policy_id):
    try:
        # 验证策略是否属于当前用户
        policy = ScanPolicy.query.filter_by(
            id=policy_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not policy:
            return jsonify({'error': '策略不存在或无权访问'}), 404
            
        # 获取该策略的所有任务
        jobs = ScanJob.query.filter_by(
            policy_id=policy_id,
            user_id=current_user.id
        ).order_by(ScanJob.created_at.desc()).all()

        return jsonify({
            'jobs': [{
                'id': job.id,
                'status': job.status,
                'progress': job.progress,
                'machines_found': job.machines_found,
                'start_time': job.start_time.isoformat() if job.start_time else None,
                'end_time': job.end_time.isoformat() if job.end_time else None,
                'error_message': job.error_message,
                'subnets': ScanSubnet.query.filter_by(id=job.subnet_id, deleted=False).first().to_dict()
            } for job in jobs]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500