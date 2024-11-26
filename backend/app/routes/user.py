from flask import Blueprint, jsonify, request
from backend.app.models import db, IP, User, ActionLog
from backend.app.auth import token_required, admin_required, generate_token
from datetime import datetime
import re

api_bp = Blueprint('api', __name__)

# Helper function for validating email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_update_data(data):
    required_fields = ['device_name', 'device_type', "os_type", 
                       'manufacturer', 'model', 'purpose']
    for field in required_fields:
        if not data.get(field):
            return f"{field} is required"
    return None

def log_action_to_db(user, action, target, details=None):
    """
    记录用户操作日志到数据库

    :param user: 当前操作的用户对象
    :param action: 操作描述，例如 "Updated IP"
    :param target: 操作的目标，例如 IP 的唯一标识
    :param details: 可选，操作的额外细节描述
    """
    source_ip = request.remote_addr
    log = ActionLog(
        user_id=user.id,
        action=action,
        target=target,
        details=details,
        source_ip = request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

@api_bp.route('/users', methods=['POST'])
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
    if not is_valid_email(email):
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
    log_action_to_db(
        user=current_user,
        action="Added a new user",
        target=new_user.id,
        details=f"User added with username: {username}, email: {email}, is_admin: {is_admin}"
    )

    return jsonify({'message': 'User added successfully', 'user': new_user.to_dict()}), 201


@api_bp.route('/users', methods=['GET'])
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
    log_action_to_db(
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

@api_bp.route('/users/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    # 记录日志
    log_action_to_db(
        user=current_user,
        action="Viewed own profile",
        target=current_user.id,
        details="User accessed their own profile"
    )
    return jsonify(current_user.to_dict())

@api_bp.route('/auth/register', methods=['POST'])
@token_required
def register_user():
    data = request.json

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Username, email, and password are required'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # 记录日志
    log_action_to_db(
        user=None,  # 注册时没有用户登录
        action="Registered a new user",
        target=user.id,
        details=f"New user registered with username: {username} and email: {email}"
    )
    return jsonify(user.to_dict()), 201

@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        token = generate_token(user.id)
        # 记录日志
        log_action_to_db(
            user=user,
            action="User logged in",
            target=user.id,
            details="Successful login"
        )
        return jsonify({'token': token, 'user': user.to_dict()})

    # 记录日志（登录失败）
    log_action_to_db(
        user=None,
        action="Failed login attempt",
        target=data.get('username'),
        details="Invalid credentials provided"
    )
    return jsonify({'message': 'Invalid credentials'}), 401

@api_bp.route('/ips', methods=['GET'])
@token_required
def get_ips(current_user):
    """
    获取 IP 列表，支持分页和全量模式。
    """
    # 获取分页参数，如果没有传递分页参数，默认为 None（全量模式）
    page = request.args.get('page', type=int)
    page_size = request.args.get('page_size', type=int)

    try:
        if page and page_size:
            # 分页模式
            ips_query = IP.query.filter_by(deleted=False)
            ips_paginated = ips_query.paginate(page=page, per_page=page_size, error_out=False)

            # 如果当前页无数据
            if not ips_paginated.items:
                return jsonify({
                    "error": "No data found for the given page.",
                    "total": ips_paginated.total,
                    "pages": ips_paginated.pages,
                    "current_page": ips_paginated.page,
                    "page_size": page_size
                }), 404

            # 日志记录
            log_action_to_db(
                user=current_user,
                action="Viewed paginated IPs",
                target="ips",
                details=f"User fetched page {page} with page_size {page_size}."
            )

            return jsonify({
                'ips': [ip.to_dict() for ip in ips_paginated.items],
                'total': ips_paginated.total,
                'pages': ips_paginated.pages,
                'current_page': ips_paginated.page,
                'page_size': page_size
            })

        else:
            # 全量模式
            ips = IP.query.filter_by(deleted=False).all()

            # 日志记录
            log_action_to_db(
                user=current_user,
                action="Viewed all IPs",
                target="ips",
                details="User fetched all IP records."
            )

            return jsonify([ip.to_dict() for ip in ips])

    except Exception as e:
        # 异常捕获并返回错误信息
        return jsonify({"error": f"Failed to fetch IPs: {str(e)}"}), 500

@api_bp.route('/ips/<ip_id>/claim', methods=['POST'])
@token_required
def claim_ip(current_user, ip_id):
    ip = IP.query.get_or_404(ip_id)

    if ip.status != 'unclaimed':
        return jsonify({'error': 'IP is already claimed'}), 400

    data = request.json
    ip.device_name = data.get('device_name')
    ip.device_type = data.get('device_type')
    ip.manufacturer = data.get('manufacturer')
    ip.model = data.get('model')
    ip.purpose = data.get('purpose')
    ip.status = 'active'
    ip.assigned_user_id = current_user.id

    db.session.commit()

    # 记录日志
    log_action_to_db(
        user=current_user,
        action="Claimed IP",
        target=ip.id,
        details=f"IP {ip.ip_address} claimed with device details: {data}"
    )
    return jsonify(ip.to_dict())

@api_bp.route('/ips/<ip_id>', methods=['POST'])
@token_required
def update_ip(current_user, ip_id):
    ip = IP.query.get_or_404(ip_id)

    # 如果是普通用户，且 IP 的 assigned_user_id 为空，则允许他们编辑（自动分配给当前用户）
    if not current_user.is_admin:
        if ip.assigned_user_id is None:
            ip.assigned_user_id = current_user.id  # 自动设置为当前用户的 ID
        elif ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'You do not have permission to update this IP'}), 403

    data = request.json

    # 如果 assigned_user_id 为空或者未提供，设置为当前用户的 ID（对于非管理员用户）
    assigned_user_id = data.get('assigned_user_id')
    if assigned_user_id in [None, ""]:
        if current_user.is_admin:
            ip.assigned_user_id = None  # 管理员可以清空 assigned_user_id
        else:
            ip.assigned_user_id = current_user.id  # 非管理员则设置为当前用户的 ID
    else:
        ip.assigned_user_id = assigned_user_id

    validation_error = validate_update_data(data)
    if validation_error:
        return jsonify({'error': validation_error}), 400

    if 'device_name' in data:
        ip.device_name = data['device_name']
    if 'device_type' in data:
        ip.device_type = data['device_type']
    if 'os_type' in data:
        ip.os_type = data['os_type']
    if 'manufacturer' in data:
        ip.manufacturer = data.get('manufacturer', ip.manufacturer)
    if 'model' in data:
        ip.model = data.get('model', ip.model)
    if 'purpose' in data:
        ip.purpose = data.get('purpose', ip.purpose)

    if ip.status != 'active':
        ip.status = 'active'

    db.session.commit()

    # 记录日志
    log_action_to_db(
        user=current_user,
        action=f"Updated IP {ip.ip_address}",
        target=ip.id,
        details=f"Updated fields: {', '.join(data.keys())}"
    )
    return jsonify(ip.to_dict()), 200