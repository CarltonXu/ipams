from flask import Blueprint, jsonify, request
from backend.app.models import db, User
from backend.app.utils.auth import token_required, admin_required, generate_token
from backend.app.utils import utils
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
@token_required
def register_user():
    data = request.json

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Username, email, and password are required'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not utils.is_valid_email(email):
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
    utils.log_action_to_db(
        user=None,  # 注册时没有用户登录
        action="Registered a new user",
        target=user.id,
        details=f"New user registered with username: {username} and email: {email}"
    )
    return jsonify(user.to_dict()), 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        token = generate_token(user.id)
        # 记录日志
        utils.log_action_to_db(
            user=user,
            action="User logged in",
            target=user.id,
            details="Successful login"
        )
        return jsonify({'token': token, 'user': user.to_dict()})

    # 记录日志（登录失败）
    utils.log_action_to_db(
        user=None,
        action="Failed login attempt",
        target=data.get('username'),
        details="Invalid credentials provided"
    )
    return jsonify({'message': 'Invalid credentials'}), 401