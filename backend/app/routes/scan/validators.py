import ipaddress
from flask import jsonify, request
from functools import wraps

def validate_subnet(subnet):
    """Validate IPv4 subnet format"""
    try:
        ipaddress.IPv4Network(subnet)
        return True
    except ValueError:
        return False

def validate_scan_schedule(schedule_type):
    """Validate scan schedule type"""
    valid_schedules = ['每分钟', '每小时', '每天', '每周', '每月', '自定义']
    return schedule_type in valid_schedules

def validate_scan_request(f):
    """Decorator to validate scan request data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        subnet = data.get('subnet')
        if subnet and not validate_subnet(subnet):
            return jsonify({'error': 'Invalid subnet format'}), 400
            
        schedule_type = data.get('schedule_type')
        if schedule_type and not validate_scan_schedule(schedule_type):
            return jsonify({'error': 'Invalid schedule type'}), 400
            
        return f(*args, **kwargs)
    return decorated_function

def validate_policy_config(data):
    """Validate policy configuration data"""
    if not isinstance(data.get('subnets'), list):
        return False, 'Subnets must be a list'
        
    if not isinstance(data.get('policies'), list):
        return False, 'Policies must be a list'
        
    # 验证每个网段
    for subnet in data.get('subnets', []):
        if not validate_subnet(subnet.get('subnet')):
            return False, f'Invalid subnet format: {subnet.get("subnet")}'
            
    return True, None

def validate_config_request(f):
    """Decorator to validate configuration request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        is_valid, error = validate_policy_config(data)
        if not is_valid:
            return jsonify({'error': error}), 400
            
        return f(*args, **kwargs)
    return decorated_function