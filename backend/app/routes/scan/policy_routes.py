from flask import Blueprint, request, jsonify
from app.models.models import db, ScanPolicy, ScanSubnet, ScanJob
from app.utils.auth import token_required
from sqlalchemy.exc import IntegrityError
from app.scheduler import scheduler
import json

policy_bp = Blueprint('policy', __name__)

@policy_bp.route('/policies', methods=['GET'])
@token_required
def get_policies(current_user):
    """Get all scan policies with their associated subnets"""
    try:
        # 获取所有未删除的策略
        policies = ScanPolicy.query.filter_by(
            user_id=current_user.id,
            deleted=False
        ).all()
        
        result = []
        for policy in policies:
            try:
                # 解析策略配置
                strategies = json.loads(policy.strategies) if policy.strategies else []
                
                # 构建策略数据
                policy_data = {
                    "id": policy.id,
                    "name": policy.name,
                    "description": policy.description,
                    "strategies": strategies,
                    "threads": policy.threads,
                    "status": policy.status,
                    "created_at": policy.created_at.isoformat() if policy.created_at else None,
                    "subnets": [
                        {
                            "id": subnet.id,
                            "name": subnet.name,
                            "subnet": subnet.subnet
                        } for subnet in policy.subnets
                    ]
                }
                result.append(policy_data)
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
        
        saved_policies = []
        for policy_data in data.get('policies', []):
            policy_name = policy_data['name']
            
            # 获取所有子网名称
            subnet_names = [subnet['name'] for subnet in data.get('subnets', [])]
            print(f"Processing policy {policy_name} with subnets: {subnet_names}")
            
            # 生成子网ID列表
            subnet_id_list = [str(subnet_map[name]) for name in subnet_names if name in subnet_map]
            
            # 处理策略数据
            strategies = []
            for strategy in policy_data.get('strategies', []):
                if strategy.get('cron') and strategy.get('start_time'):
                    strategies.append({
                        'cron': strategy['cron'],
                        'start_time': strategy['start_time'],
                        'subnet_ids': subnet_id_list,
                        'scan_params': strategy['scan_params'],
                    })
            
            if not strategies:  # 如果没有有效的策略配置，跳过这个策略
                print(f"No valid strategies for policy {policy_name}")
                continue
            
            if policy_name in existing_policies:
                policy = existing_policies[policy_name]
                policy.description = policy_data['description']
                policy.strategies = json.dumps(strategies)
                policy.threads = policy_data.get('threads', 5)
            else:
                policy = ScanPolicy(
                    name=policy_name,
                    description=policy_data['description'],
                    threads=policy_data.get('threads', 5),
                    user_id=current_user.id,
                    strategies=strategies
                )
                db.session.add(policy)
            
            # 建立策略和子网的关联关系
            policy.subnets = []
            for subnet_data in data.get('subnets', []):
                subnet = ScanSubnet.query.filter_by(
                    subnet=subnet_data['subnet'],
                    user_id=current_user.id,
                    deleted=False
                ).first()
                if subnet:
                    policy.subnets.append(subnet)
            
            saved_policies.append(policy)
        
        db.session.commit()
        
        # 更新调度器
        for policy in saved_policies:
            scheduler.update_policy(policy.id)
        
        # 返回保存的策略信息
        return jsonify({
            'message': 'Configuration saved successfully',
            'policies': [{
                'id': policy.id,
                'name': policy.name,
                'description': policy.description,
                'strategies': json.loads(policy.strategies),
                'threads': policy.threads,
                'status': policy.status,
                'created_at': policy.created_at.isoformat() if policy.created_at else None,
                'subnets': [{
                    'id': subnet.id,
                    'name': subnet.name,
                    'subnet': subnet.subnet
                } for subnet in policy.subnets]
            } for policy in saved_policies]
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
    try:
        policy = ScanPolicy.query.filter_by(
            id=policy_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not policy:
            return jsonify({'error': 'Policy not found'}), 404
            
        data = request.json
        
        # 处理子网更新
        if 'subnets' in data:
            # 清空现有的子网关联
            policy.subnets = []
            
            # 处理每个子网
            for subnet_data in data['subnets']:
                # 查找或创建子网
                subnet = ScanSubnet.query.filter_by(
                    subnet=subnet_data['subnet'],
                    user_id=current_user.id,
                    deleted=False
                ).first()
                
                if not subnet:
                    # 创建新子网
                    subnet = ScanSubnet(
                        name=subnet_data['name'],
                        subnet=subnet_data['subnet'],
                        user_id=current_user.id
                    )
                    db.session.add(subnet)
                    db.session.flush()  # 获取新子网的ID
                
                # 更新子网名称
                subnet.name = subnet_data['name']
                
                # 添加到策略的子网关联中
                policy.subnets.append(subnet)
        
        # 更新基本信息
        policy.name = data.get('name', policy.name)
        policy.description = data.get('description', policy.description)
        policy.threads = data.get('threads', policy.threads)
        
        # 更新策略配置
        if 'strategies' in data:
            strategies = data['strategies']
            # 验证策略数据
            for strategy in strategies:
                if not all(key in strategy for key in ['cron', 'start_time', 'scan_params']):
                    return jsonify({'error': 'Invalid strategy format'}), 400
                
                # 处理子网ID列表
                subnet_ids = strategy.get('subnet_ids', [])
                if not isinstance(subnet_ids, list):
                    return jsonify({'error': 'subnet_ids must be a list'}), 400
                
                # 过滤掉空值
                subnet_ids = [id for id in subnet_ids if id is not None]
                
                # 如果子网ID列表为空，使用策略关联的所有子网ID
                if not subnet_ids:
                    subnet_ids = [subnet.id for subnet in policy.subnets]
                
                # 验证所有子网ID是否属于当前策略
                valid_subnet_ids = [subnet.id for subnet in policy.subnets]
                for subnet_id in subnet_ids:
                    if subnet_id not in valid_subnet_ids:
                        return jsonify({'error': f'Subnet {subnet_id} not associated with this policy'}), 400
                
                # 更新策略的子网ID
                strategy['subnet_ids'] = subnet_ids
            
            # 更新策略
            policy.strategies = json.dumps(strategies)
        
        db.session.commit()
        
        # 更新调度器
        scheduler.update_policy(policy.id)
        
        # 获取更新后的策略信息
        updated_policy = policy.to_dict()
        
        # 添加子网信息
        updated_policy['subnets'] = [
            {
                'id': subnet.id,
                'name': subnet.name,
                'subnet': subnet.subnet
            } for subnet in policy.subnets
        ]
        
        return jsonify({
            'message': 'Policy updated successfully',
            'policy': updated_policy
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating policy: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    
    # 从调度器中移除策略
    scheduler.remove_policy(policy_id)
    
    # 软删除策略
    policy.deleted = True
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
                'subnets': job.subnet.to_dict() if job.subnet else None
            } for job in jobs]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取所有定时任务信息
@policy_bp.route('/policies/scheduler/jobs', methods=['GET'])
@token_required
def get_scheduler_jobs(current_user):
    """Get all scheduled jobs information"""
    try:
        jobs = scheduler.scheduler.get_jobs()
        jobs_info = []
        
        for job in jobs:
            # 解析策略ID
            policy_id = job.id.split('_')[0]
            
            # 获取策略信息
            policy = ScanPolicy.query.filter_by(
                id=policy_id,
                user_id=current_user.id,
                deleted=False
            ).first()
            
            if not policy:
                continue
            
            job_info = {
                'id': job.id,
                'policy_id': policy_id,
                'policy_name': policy.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'is_start_job': '_start' in job.id
            }
            jobs_info.append(job_info)
        
        return jsonify(jobs_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更新策略状态
@policy_bp.route('/policies/<policy_id>/status', methods=['PUT'])
@token_required
def update_policy_status(current_user, policy_id):
    """Update policy status (enable/disable)"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['active', 'inactive']:
            return jsonify({'error': 'Invalid status'}), 400
            
        policy = ScanPolicy.query.filter_by(
            id=policy_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not policy:
            return jsonify({'error': '策略不存在或无权访问'}), 404
            
        policy.status = new_status
        db.session.commit()
        
        # 如果禁用策略，从调度器中移除
        if new_status == 'inactive':
            scheduler.remove_policy(policy_id)
        # 如果启用策略，重新调度
        else:
            scheduler.schedule_policy(policy)
            
        return jsonify({'message': '策略状态更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500