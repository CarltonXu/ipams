from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename
from backend.app.models import db, User, IP
from backend.app.utils.auth import token_required, admin_required, generate_token
from backend.app.utils import utils
import os
import uuid

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
    avatar = "/src/assets/avatar.jpeg"

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
        is_admin=is_admin,
        avatar=avatar
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

# 上传头像
@user_bp.route('/users/upload-avatar', methods=['POST'])
@token_required
def upload_avatar(current_user):
    """上传用户头像"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not utils.allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
        return jsonify({'error': 'File type not allowed'}), 400

    # 使用 secure_filename 处理原始文件名，但只是为了安全检查
    secure_name = secure_filename(file.filename)
    if not secure_name:
        return jsonify({'error': 'Invalid filename'}), 400
        
    try:
        # 1. 获取文件扩展名
        original_ext = os.path.splitext(file.filename)[1].lower()

        # 2. 生成新的文件名（使用 UUID + 原始扩展名）
        unique_filename = f"{uuid.uuid4()}{original_ext}"
        
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 更新用户头像路径
        avatar_url = f"/uploads/avatars/{unique_filename}"

        User.query.filter_by(id=current_user.id).update({
            'avatar': avatar_url
        })

        db.session.commit()
        
        # 记录日志
        utils.log_action_to_db(
            user=current_user,
            action="Updated avatar",
            target=current_user.id,
            details=f"Avatar updated to: {avatar_url}"
        )
        
        return jsonify({
            'message': 'Avatar uploaded successfully',
            'url': avatar_url
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
    query = request.args.get('query')
    column = request.args.get('column')
    is_admin_str = request.args.get('is_admin')
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    no_pagination = request.args.get('no_pagination', type=lambda x: x.lower() == 'true', default=False)

    
    is_admin = None
    if is_admin_str is not None:
        if is_admin_str.lower() == 'true':
            is_admin = True
        elif is_admin_str.lower() == 'false':
            is_admin = False
    
    try:
        users_query = User.query.filter_by(deleted=False)

        if query and column:
            if column == 'username':
                users_query = users_query.filter(User.username.ilike(f'%{query}%'))
            elif column == "id":
                users_query = users_query.filter(User.id == query)
            elif column == 'email':
                users_query = users_query.filter(User.email.ilike(f'%{query}%'))
            elif column == 'is_admin':
                users_query = users_query.filter(User.is_admin == is_admin)
            elif column == 'wechat_id':
                users_query = users_query.filter(User.wechat_id.ilike(f'%{query}%'))

        if is_admin is not None:
            users_query = users_query.filter(User.is_admin == is_admin)
        
        if sort_by:
            sort_column = getattr(User, sort_by, None)
            if sort_column is not None:
                users_query = users_query.order_by(
                    desc(sort_column) if sort_order == 'desc' else asc(sort_column)
                )
        
        # 判断是否需要分页
        if no_pagination or (page is None and page_size is None):
            # 全量模式
            users = users_query.filter_by(deleted=False).all()
            return jsonify({
                'users': [user.to_dict() for user in users],
                'total': len(users),
            })
        else:
            # 使用 SQLAlchemy 的 paginate 方法
            users_paginated = users_query.paginate(
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
                'page_size': page_size,
                'current_page': users_paginated.page
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@user_bp.route('/users/check-ips', methods=['POST'])
@token_required
def check_users_ips(current_user):
    """
    检查用户关联的 IP 地址
    """
    data = request.json
    if not data or 'user_ids' not in data:
        return jsonify({'error': 'Missing user_ids parameter'}), 400

    user_ids = data['user_ids']
    users_with_ips = []

    try:
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user:
                # 获取用户关联的 IP 地址
                ips = IP.query.filter_by(
                    assigned_user_id=user_id,
                    deleted=False
                ).all()
                
                if ips:
                    users_with_ips.append({
                        'id': user.id,
                        'username': user.username,
                        'ips': [ip.to_dict() for ip in ips]
                    })

        return jsonify({
            'usersWithIPs': users_with_ips
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/batch-delete', methods=['POST'])
@token_required
@admin_required
def batch_delete_users(current_user):
    """
    批量删除用户
    - 只有管理员可以执行此操作
    - 如果用户有关联的 IP，会先检查并返回错误
    """
    data = request.json
    if not data or 'user_ids' not in data:
        return jsonify({'error': 'Missing user_ids parameter'}), 400

    user_ids = data['user_ids']

    try:
        # 检查是否有用户关联了 IP
        users_with_ips = []
        for user_id in user_ids:
            user = User.query.get(user_id)
            if not user:
                continue

            # 检查用户关联的 IP
            ips = IP.query.filter_by(
                assigned_user_id=user_id,
                deleted=False
            ).all()
            
            if ips:
                users_with_ips.append({
                    'id': user.id,
                    'username': user.username,
                    'ips': [ip.to_dict() for ip in ips]
                })

        # 如果有用户关联了 IP，返回错误
        if users_with_ips:
            return jsonify({
                'error': 'Users have associated IPs',
                'usersWithIPs': users_with_ips
            }), 400

        # 执行批量删除
        deleted_count = 0
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user.id != current_user.id:  # 不能删除自己
                user.deleted = True
                deleted_count += 1

        db.session.commit()

        # 记录日志
        utils.log_action_to_db(
            user=current_user,
            action="Batch delete users",
            target="users",
            details=f"Deleted {deleted_count} users: {', '.join(user_ids)}"
        )

        return jsonify({
            'message': f'Successfully deleted {deleted_count} users',
            'deleted_count': deleted_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500