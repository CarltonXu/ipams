from flask import Blueprint, jsonify, request
from backend.app.models import db, IP, User, ActionLog
from backend.app.utils.auth import token_required, admin_required, generate_token
from backend.app.utils import utils
from datetime import datetime
import re

ips_bp = Blueprint('ips', __name__)


@ips_bp.route('/ips', methods=['GET'])
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
            utils.log_action_to_db(
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
            utils.log_action_to_db(
                user=current_user,
                action="Viewed all IPs",
                target="ips",
                details="User fetched all IP records."
            )

            return jsonify([ip.to_dict() for ip in ips])

    except Exception as e:
        # 异常捕获并返回错误信息
        return jsonify({"error": f"Failed to fetch IPs: {str(e)}"}), 500

@ips_bp.route('/ips/<ip_id>/claim', methods=['POST'])
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
    utils.log_action_to_db(
        user=current_user,
        action="Claimed IP",
        target=ip.id,
        details=f"IP {ip.ip_address} claimed with device details: {data}"
    )
    return jsonify(ip.to_dict())

@ips_bp.route('/ips/<ip_id>', methods=['POST'])
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

    validation_error = utils.validate_update_data(data)
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
    utils.log_action_to_db(
        user=current_user,
        action=f"Updated IP {ip.ip_address}",
        target=ip.id,
        details=f"Updated fields: {', '.join(data.keys())}"
    )
    return jsonify(ip.to_dict()), 200