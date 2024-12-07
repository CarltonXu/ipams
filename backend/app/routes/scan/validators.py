import ipaddress
from flask import jsonify
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