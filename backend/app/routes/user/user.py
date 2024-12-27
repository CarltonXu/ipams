from flask import Blueprint, jsonify, request
from backend.app.models import db, User
from backend.app.utils.auth import token_required, admin_required, generate_token
from backend.app.utils import utils
import re

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
@token_required
def add_users(current_user):
    """
    管理员添加新用户。
    """
    data = request.json

    # 校验必填字段
    required_fields = ['username', 'email', 'password', 'is_admin']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    # 校验邮箱格式
    if not utils.is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    # 创建新用户
    new_user = User(
        username=username,
        email=email,
        is_admin=is_admin
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # 记录日志
    utils.log_action_to_db(
        user=current_user,
        action="Added a new user",
        target=new_user.id,
        details=f"User added with username: {username}, email: {email}, is_admin: {is_admin}"
    )

    return jsonify({'message': 'User added successfully', 'user': new_user.to_dict()}), 201

@user_bp.route('/users/<string:user_id>', methods=['DELETE'])
@token_required
def delete_users(current_user, user_id):
    # 检查是否有权限删除该用户
    if not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    # 删除用户逻辑
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.deleted = True
    db.session.commit()

    utils.log_action_to_db(
        user=current_user,
        action="Delete a user",
        target=user_id,
        details=f"User {user_id} deleted successfully"
    )
    return jsonify({'message': f'User {user_id} deleted successfully'}), 200

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    # 获取分页参数，默认值为第1页，每页10条记录
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    # 使用 SQLAlchemy 的 paginate 方法
    users_paginated = User.query.filter_by(deleted=False).paginate(
        page=page,
        per_page=page_size,
        error_out=False
    )

    # 记录日志
    utils.log_action_to_db(
        user=current_user,
        action="Viewed all users",
        target="users",
        details="User fetched the list of all users"
    )

    return jsonify({
        'users': [user.to_dict() for user in users_paginated.items],
        'total': users_paginated.total,
        'pages': users_paginated.pages,
        'current_page': users_paginated.page
    })

@user_bp.route('/users/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    # 记录日志
    utils.log_action_to_db(
        user=current_user,
        action="Viewed own profile",
        target=current_user.id,
        details="User accessed their own profile"
    )
    return jsonify(current_user.to_dict())

@user_bp.route('/users/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """
    修改用户密码
    """
    data = request.json
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
        
    # 验证旧密码
    if not current_user.check_password(data['old_password']):
        return jsonify({'error': 'Invalid old password'}), 400
        
    # 设置新密码
    current_user.set_password(data['new_password'])
    db.session.commit()
    
    # 记录日志
    utils.log_action_to_db(
        user=current_user,
        action="Changed password",
        target=current_user.id,
        details="User changed their password"
    )
    
    return jsonify({'message': 'Password changed successfully'}), 200

@user_bp.route('/users/<string:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """
    更新用户信息。
    只有管理员或用户本人可以更新信息。
    """
    # 检查权限
    if not current_user.is_admin and str(current_user.id) != user_id:
        return jsonify({'error': 'Permission denied'}), 403

    # 获取要更新的用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 允许更新的字段
    allowed_fields = ['username', 'email', 'is_admin', "wechat_id"]
    updates = {}

    for field in allowed_fields:
        if field in data:
            # 特殊处理 is_admin 字段
            if field == 'is_admin' and not current_user.is_admin:
                continue  # 非管理员不能修改管理员权限
            
            # 检查用户名和邮箱是否已存在
            if field == 'username' and data[field] != user.username:
                if User.query.filter_by(username=data[field]).first():
                    return jsonify({'error': 'Username already exists'}), 400
                    
            if field == 'email' and data[field] != user.email:
                if not utils.is_valid_email(data[field]):
                    return jsonify({'error': 'Invalid email format'}), 400
                if User.query.filter_by(email=data[field]).first():
                    return jsonify({'error': 'Email already exists'}), 400
                    
            updates[field] = data[field]

    # 如果有密码更新
    if 'password' in data and data['password'] != "":
        user.set_password(data['password'])

    # 更新用户信息
    for key, value in updates.items():
        setattr(user, key, value)

    db.session.commit()

    # 记录日志
    utils.log_action_to_db(
        user=current_user,
        action="Updated user information",
        target=user_id,
        details=f"Updated fields: {', '.join(updates.keys())}"
    )

    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    })