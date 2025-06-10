from flask import Blueprint, jsonify, request
from app.core.security.auth import token_required, admin_required
from app.models.models import db, SystemConfig
from app.core.utils.helpers import log_action_to_db

config_bp = Blueprint('config', __name__)

@config_bp.route('/config', methods=['GET'])
@token_required
def get_config(current_user):
    """获取系统配置"""
    try:
        # 获取所有配置
        configs = SystemConfig.query.all()
        
        # 根据用户角色过滤配置
        if not current_user.is_admin:
            # 非管理员只能看到公开配置
            configs = [c for c in configs if c.is_public]
        
        return jsonify({
            'configs': [config.to_dict() for config in configs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/<key>', methods=['GET'])
@token_required
def get_config_by_key(current_user, key):
    """获取指定配置项"""
    try:
        config = SystemConfig.query.filter_by(key=key).first()
        
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
            
        # 检查权限
        if not config.is_public and not current_user.is_admin:
            return jsonify({'error': 'Permission denied'}), 403
            
        return jsonify(config.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config', methods=['POST'])
@admin_required
def create_config(current_user):
    """创建新的配置项"""
    try:
        data = request.json
        
        # 验证必填字段
        required_fields = ['key', 'value', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # 检查配置是否已存在
        if SystemConfig.query.filter_by(key=data['key']).first():
            return jsonify({'error': 'Configuration key already exists'}), 400
            
        # 创建新配置
        config = SystemConfig(
            key=data['key'],
            value=data['value'],
            description=data['description'],
            is_public=data.get('is_public', False)
        )
        
        db.session.add(config)
        db.session.commit()
        
        # 记录操作日志
        log_action_to_db(
            user=current_user,
            action="Create configuration",
            target=config.key,
            details=f"Created new configuration: {config.key}"
        )
        
        return jsonify(config.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/<key>', methods=['PUT'])
@admin_required
def update_config(current_user, key):
    """更新配置项"""
    try:
        config = SystemConfig.query.filter_by(key=key).first()
        
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
            
        data = request.json
        
        # 更新配置
        if 'value' in data:
            config.value = data['value']
        if 'description' in data:
            config.description = data['description']
        if 'is_public' in data:
            config.is_public = data['is_public']
            
        db.session.commit()
        
        # 记录操作日志
        log_action_to_db(
            user=current_user,
            action="Update configuration",
            target=config.key,
            details=f"Updated configuration: {config.key}"
        )
        
        return jsonify(config.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/<key>', methods=['DELETE'])
@admin_required
def delete_config(current_user, key):
    """删除配置项"""
    try:
        config = SystemConfig.query.filter_by(key=key).first()
        
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
            
        # 记录操作日志
        log_action_to_db(
            user=current_user,
            action="Delete configuration",
            target=config.key,
            details=f"Deleted configuration: {config.key}"
        )
        
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({'message': 'Configuration deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 