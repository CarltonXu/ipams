from flask import request
from backend.app.models import db, ActionLog
import re

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