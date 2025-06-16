from flask import request
from PIL import Image, ImageDraw, ImageFont
from app.models.models import db, ActionLog, SystemMetrics, NetworkMetrics, DiskMetrics, ProcessMetrics
import re
import uuid
import random
import string
import socket
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
    """获取系统资源使用情况"""
    try:
        # 获取系统基础指标
        cpu_info = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # 系统负载
        load_avg = psutil.getloadavg()
        
        # 进程信息 - 使用更安全的方式获取
        process_count = len(psutil.pids())
        thread_count = 0
        try:
            for proc in psutil.process_iter(['num_threads']):
                try:
                    thread_count += proc.info['num_threads']
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"获取线程数时发生错误: {str(e)}")
            thread_count = 0
        
        # 创建系统基础指标记录
        system_metrics = SystemMetrics(
            cpu_usage=cpu_usage,
            cpu_count=cpu_count,
            cpu_freq=cpu_info.current if cpu_info else 0,
            memory_total=memory.total,
            memory_used=memory.used,
            memory_free=memory.free,
            memory_usage=memory.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_free=swap.free,
            load_avg_1min=load_avg[0],
            load_avg_5min=load_avg[1],
            load_avg_15min=load_avg[2],
            process_count=process_count,
            thread_count=thread_count
        )
        db.session.add(system_metrics)
        
        # 获取网络接口指标
        try:
            net_io_counters = psutil.net_io_counters(pernic=True)
            net_if_stats = psutil.net_if_stats()
            
            for interface, stats in net_if_stats.items():
                if interface in net_io_counters:
                    io = net_io_counters[interface]
                    net_metrics = NetworkMetrics(
                        interface=interface,
                        bytes_sent=io.bytes_sent,
                        bytes_recv=io.bytes_recv,
                        packets_sent=io.packets_sent,
                        packets_recv=io.packets_recv,
                        errin=io.errin,
                        errout=io.errout,
                        dropin=io.dropin,
                        dropout=io.dropout,
                        is_up=stats.isup,
                        speed=stats.speed,
                        mtu=stats.mtu
                    )
                    db.session.add(net_metrics)
        except Exception as e:
            print(f"获取网络指标时发生错误: {str(e)}")
        
        # 获取磁盘指标
        try:
            disk_partitions = psutil.disk_partitions()
            disk_io_counters = psutil.disk_io_counters(perdisk=True)
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    device = partition.device
                    
                    # 获取磁盘IO信息
                    io = disk_io_counters.get(device.split('/')[-1], None)
                    
                    disk_metrics = DiskMetrics(
                        device=device,
                        mountpoint=partition.mountpoint,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        usage=usage.percent,
                        read_bytes=io.read_bytes if io else 0,
                        write_bytes=io.write_bytes if io else 0,
                        read_count=io.read_count if io else 0,
                        write_count=io.write_count if io else 0,
                        read_time=io.read_time if io else 0,
                        write_time=io.write_time if io else 0,
                        is_removable=partition.fstype in ['vfat', 'exfat', 'ntfs'],
                        fstype=partition.fstype
                    )
                    db.session.add(disk_metrics)
                except Exception as e:
                    print(f"获取磁盘 {partition.mountpoint} 指标时发生错误: {str(e)}")
                    continue
        except Exception as e:
            print(f"获取磁盘指标时发生错误: {str(e)}")
        
        # 获取进程指标 - 使用更安全的方式
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time', 'num_threads']):
                try:
                    if proc.info['pid'] == 0:  # 跳过 pid=0 的进程
                        continue
                        
                    with proc.oneshot():
                        process_metrics = ProcessMetrics(
                            pid=proc.info['pid'],
                            name=proc.info['name'],
                            cpu_percent=proc.info['cpu_percent'],
                            cpu_times_user=proc.cpu_times().user,
                            cpu_times_system=proc.cpu_times().system,
                            memory_percent=proc.info['memory_percent'],
                            memory_rss=proc.memory_info().rss,
                            memory_vms=proc.memory_info().vms,
                            status=proc.info['status'],
                            create_time=datetime.fromtimestamp(proc.info['create_time']),
                            num_threads=proc.info['num_threads'],
                            num_fds=proc.num_fds() if hasattr(proc, 'num_fds') else None
                        )
                        db.session.add(process_metrics)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, KeyError, ValueError) as e:
                    continue
        except Exception as e:
            print(f"获取进程指标时发生错误: {str(e)}")
        
        # 提交所有更改
        db.session.commit()
        
        return {
            'system': system_metrics.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        db.session.rollback()
        print(f"获取系统指标时发生错误: {str(e)}")
        return None

def get_system_info():
    """获取系统基本信息"""
    # 获取系统启动时间
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    hostname = socket.gethostname()
    
    # 返回原始数据
    return {
        'hostname': hostname,
        'ipaddress': socket.gethostbyname(hostname),
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