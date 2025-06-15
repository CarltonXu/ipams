from flask import request
from PIL import Image, ImageDraw, ImageFont
from app.models.models import db, ActionLog, SystemMetrics
import re
import uuid
import random
import string
import io
import base64
import psutil
import platform
import datetime

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

def generate_uuid():
    """生成唯一标识"""
    return str(uuid.uuid4())

def generate_captcha_code(length=4):
    """生成随机验证码"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_captcha_image(text):
    """创建验证码图片"""
    # 图片大小
    width = 120
    height = 30
    # 创建图片
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 使用自定义字体
    try:
        font = ImageFont.truetype('arial.ttf', 30)
    except:
        font = ImageFont.load_default()

    # 绘制文字
    for i, char in enumerate(text):
        # 随机颜色
        color = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))
        # 随机位置
        position = (15 + i * 25, random.randint(2, 8))
        draw.text(position, char, font=font, fill=color)

    # 添加干扰线
    for _ in range(5):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start, end], fill=(169, 169, 169), width=1)

    # 添加噪点
    for _ in range(30):
        position = (random.randint(0, width), random.randint(0, height))
        draw.point(position, fill=(169, 169, 169))

    # 转换为base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{image_str}"

def log_action_to_db(user, action, target, details=None):
    """
    记录用户操作日志到数据库

    :param user: 当前操作的用户对象
    :param action: 操作描述，例如 "Updated IP"
    :param target: 操作的目标，例如 IP 的唯一标识
    :param details: 可选，操作的额外细节描述
    """
    # 没有 user.id, 则记录为匿名用户
    if not user:
        user_id = "Anonymous"
    else:
        user_id = user.id

    source_ip = request.remote_addr
    log = ActionLog(
        user_id=user_id,
        action=action,
        target=target,
        details=details,
        source_ip = source_ip
    )
    db.session.add(log)
    db.session.commit()

def allowed_file(filename, allowed_extensions):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')

    return {
        'cpu': cpu_usage,
        'memory': memory_info.percent,
        'disk': disk_info.percent
    }

def get_system_metrics():
    """获取系统资源使用情况"""
    try:
        # CPU 使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        memory_total = memory.total
        memory_used = memory.used
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        disk_total = disk.total
        disk_used = disk.used
        
        # 创建新的监控记录
        metrics = SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            memory_total=memory_total,
            memory_used=memory_used,
            disk_total=disk_total,
            disk_used=disk_used
        )
        
        db.session.add(metrics)
        db.session.commit()
        
        return metrics.to_dict()
    except Exception as e:
        db.session.rollback()
        raise e

def get_system_info():
    """获取系统基本信息"""
    # 获取系统启动时间
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    
    # 返回原始数据
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'uptime': {
            'days': uptime.days,
            'hours': uptime.seconds // 3600,
            'minutes': (uptime.seconds % 3600) // 60
        }
    }

def cleanup_old_metrics(days=7):
    """清理旧的监控数据"""
    from datetime import datetime, timedelta
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        SystemMetrics.query.filter(SystemMetrics.timestamp < cutoff_date).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e 