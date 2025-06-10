from flask import Blueprint, jsonify, request
from app.models.models import db, User
from app.core.security.auth import generate_token, token_required
from app.core.utils import helpers
from app.services.redis.manager import RedisManager

import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/captcha', methods=['GET'])
def get_captcha():
    """获取验证码"""
    # 生成验证码
    captcha_text = helpers.generate_captcha_code()
    captcha_key = helpers.generate_uuid()  # 生成唯一标识
    
    # 生成验证码图片
    captcha_image = helpers.create_captcha_image(captcha_text)
    
    # 使用RedisManager存储验证码
    if not RedisManager.set_with_ttl(f"captcha:{captcha_key}", captcha_text, 300):
        return jsonify({'message': 'Failed to generate captcha'}), 500
    
    return jsonify({
        'captchaKey': captcha_key,
        'captchaImage': captcha_image
    })

@auth_bp.route('/auth/register', methods=['POST'])
def register_user():
    data = request.json

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Username, email, and password are required'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not helpers.is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json

    # 验证必填字段
    if not all(k in data for k in ['username', 'password', 'captcha', 'captchaKey']):
        return jsonify({'message': 'Missing required fields'}), 400

    # 验证验证码
    captcha_key = data.get('captchaKey')
    captcha_text = data.get('captcha').upper() # 转换为大写进行验证

    # 使用RedisManager获取验证码
    stored_captcha = RedisManager.get(f"captcha:{captcha_key}")
    if not stored_captcha or stored_captcha != captcha_text:
        return jsonify({'message': 'Invalid or expired captcha'}), 400

    # 删除已经使用的验证码
    RedisManager.delete(f"captcha:{captcha_key}")

    # 验证用户名和密码
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        token = generate_token(user.id)
        # 记录日志
        helpers.log_action_to_db(
            user=user,
            action="User logged in",
            target=user.id,
            details="Successful login"
        )
        return jsonify({'token': token, 'user': user.to_dict()})

    # 记录日志（登录失败）
    helpers.log_action_to_db(
        user=user,
        action="Failed login attempt",
        target=data.get('username'),
        details="Invalid credentials or captcha"
    )
    return jsonify({'message': 'Invalid username or password'}), 401

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    pass

@auth_bp.route('/auth/refresh', methods=['POST'])
@token_required
def refresh():
    pass