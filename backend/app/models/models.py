from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(100))
    wechat_id = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db. Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)

    # 添加关系
    scan_subnets = relationship('ScanSubnet', back_populates='user', cascade='all, delete-orphan')
    scan_policies = relationship('ScanPolicy', back_populates='user', cascade='all, delete-orphan')
    scan_jobs = relationship('ScanJob', back_populates='user', cascade='all, delete-orphan')
    action_logs = relationship('ActionLog', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'wechat_id': self.wechat_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'deleted': self.deleted
        }

class IP(db.Model):
    __tablename__ = 'ips'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    ip_address = db.Column(db.String(15), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='unclaimed')
    assigned_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)  # 外键引用
    device_name = db.Column(db.String(255))
    device_type = db.Column(db.String(50))
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    os_type = db.Column(db.Enum('Linux', 'Windows', 'Other', name='os_type_enum'), nullable=False, default='Other')
    purpose = db.Column(db.Text)
    location = db.Column(db.String(255))
    last_scanned = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)

    assigned_user = db.relationship('User', backref='assigned_ips', single_parent=True)

    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'device_name': self.device_name or '',
            'device_type': self.device_type or '',
            'manufacturer': self.manufacturer or '',
            'model': self.model or '',
            'os_type': self.os_type,
            'purpose': self.purpose or '',
            'location': self.location or '',
            'last_scanned': self.last_scanned.isoformat() if self.last_scanned else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'assigned_user': self.assigned_user.to_dict() if self.assigned_user else None
        }

class SystemMetrics(db.Model):
    """系统基础资源监控"""
    __tablename__ = 'system_metrics'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # CPU 使用率
    cpu_usage = db.Column(db.Float, nullable=False)  # CPU 使用率百分比
    cpu_count = db.Column(db.Integer, nullable=False)  # CPU 核心数
    cpu_freq = db.Column(db.Float, nullable=False)  # CPU 频率 (MHz)
    
    # 内存使用情况
    memory_total = db.Column(db.BigInteger, nullable=False)  # 总内存（字节）
    memory_used = db.Column(db.BigInteger, nullable=False)   # 已用内存（字节）
    memory_free = db.Column(db.BigInteger, nullable=False)   # 空闲内存（字节）
    memory_usage = db.Column(db.Float, nullable=False)      # 内存使用率百分比
    swap_total = db.Column(db.BigInteger, nullable=False)    # 交换分区总大小
    swap_used = db.Column(db.BigInteger, nullable=False)     # 交换分区已用大小
    swap_free = db.Column(db.BigInteger, nullable=False)     # 交换分区空闲大小
    
    # 系统负载
    load_avg_1min = db.Column(db.Float, nullable=False)     # 1分钟负载
    load_avg_5min = db.Column(db.Float, nullable=False)     # 5分钟负载
    load_avg_15min = db.Column(db.Float, nullable=False)    # 15分钟负载
    
    # 进程信息
    process_count = db.Column(db.Integer, nullable=False)    # 进程总数
    thread_count = db.Column(db.Integer, nullable=False)     # 线程总数

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'cpu': {
                'usage': self.cpu_usage,
                'count': self.cpu_count,
                'frequency': self.cpu_freq
            },
            'memory': {
                'total': self.memory_total,
                'used': self.memory_used,
                'free': self.memory_free,
                'usage': self.memory_usage,
                'swap': {
                    'total': self.swap_total,
                    'used': self.swap_used,
                    'free': self.swap_free
                }
            },
            'load': {
                '1min': self.load_avg_1min,
                '5min': self.load_avg_5min,
                '15min': self.load_avg_15min
            },
            'process': {
                'count': self.process_count,
                'thread_count': self.thread_count
            }
        }

    @classmethod
    def get_latest_metrics(cls):
        return cls.query.order_by(cls.timestamp.desc()).first()

    @classmethod
    def get_metrics_history(cls, hours=24):
        """获取指定小时数内的监控数据"""
        from datetime import datetime, timedelta
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(cls.timestamp >= start_time).order_by(cls.timestamp.asc()).all() 

class NetworkMetrics(db.Model):
    """网络接口监控"""
    __tablename__ = 'network_metrics'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    interface = db.Column(db.String(50), nullable=False)  # 网卡名称
    
    # 网络流量
    bytes_sent = db.Column(db.BigInteger, nullable=False)      # 发送的字节数
    bytes_recv = db.Column(db.BigInteger, nullable=False)      # 接收的字节数
    packets_sent = db.Column(db.BigInteger, nullable=False)    # 发送的数据包数
    packets_recv = db.Column(db.BigInteger, nullable=False)    # 接收的数据包数
    
    # 网络错误
    errin = db.Column(db.Integer, nullable=False)             # 接收错误数
    errout = db.Column(db.Integer, nullable=False)            # 发送错误数
    dropin = db.Column(db.Integer, nullable=False)            # 接收丢包数
    dropout = db.Column(db.Integer, nullable=False)           # 发送丢包数
    
    # 网络状态
    is_up = db.Column(db.Boolean, nullable=False)             # 网卡是否启用
    speed = db.Column(db.Integer, nullable=True)              # 网卡速度 (Mbps)
    mtu = db.Column(db.Integer, nullable=True)                # MTU 值

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'interface': self.interface,
            'traffic': {
                'bytes_sent': self.bytes_sent,
                'bytes_recv': self.bytes_recv,
                'packets_sent': self.packets_sent,
                'packets_recv': self.packets_recv
            },
            'errors': {
                'errin': self.errin,
                'errout': self.errout,
                'dropin': self.dropin,
                'dropout': self.dropout
            },
            'status': {
                'is_up': self.is_up,
                'speed': self.speed,
                'mtu': self.mtu
            }
        }

class DiskMetrics(db.Model):
    """磁盘分区监控"""
    __tablename__ = 'disk_metrics'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    device = db.Column(db.String(50), nullable=False)  # 设备名称
    mountpoint = db.Column(db.String(255), nullable=False)  # 挂载点
    
    # 磁盘使用情况
    total = db.Column(db.BigInteger, nullable=False)    # 总空间（字节）
    used = db.Column(db.BigInteger, nullable=False)     # 已用空间（字节）
    free = db.Column(db.BigInteger, nullable=False)     # 空闲空间（字节）
    usage = db.Column(db.Float, nullable=False)         # 使用率百分比
    
    # 磁盘IO
    read_bytes = db.Column(db.BigInteger, nullable=False)    # 读取字节数
    write_bytes = db.Column(db.BigInteger, nullable=False)   # 写入字节数
    read_count = db.Column(db.BigInteger, nullable=False)    # 读取次数
    write_count = db.Column(db.BigInteger, nullable=False)   # 写入次数
    read_time = db.Column(db.BigInteger, nullable=False)     # 读取时间（毫秒）
    write_time = db.Column(db.BigInteger, nullable=False)    # 写入时间（毫秒）
    
    # 磁盘状态
    is_removable = db.Column(db.Boolean, nullable=False)     # 是否可移动设备
    fstype = db.Column(db.String(50), nullable=True)         # 文件系统类型

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'device': self.device,
            'mountpoint': self.mountpoint,
            'usage': {
                'total': self.total,
                'used': self.used,
                'free': self.free,
                'usage': self.usage
            },
            'io': {
                'read_bytes': self.read_bytes,
                'write_bytes': self.write_bytes,
                'read_count': self.read_count,
                'write_count': self.write_count,
                'read_time': self.read_time,
                'write_time': self.write_time
            },
            'status': {
                'is_removable': self.is_removable,
                'fstype': self.fstype
            }
        }

class ProcessMetrics(db.Model):
    """进程监控"""
    __tablename__ = 'process_metrics'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pid = db.Column(db.Integer, nullable=False)  # 进程ID
    name = db.Column(db.String(255), nullable=False)  # 进程名称
    
    # CPU 使用情况
    cpu_percent = db.Column(db.Float, nullable=False)  # CPU 使用率
    cpu_times_user = db.Column(db.Float, nullable=False)  # 用户态 CPU 时间
    cpu_times_system = db.Column(db.Float, nullable=False)  # 系统态 CPU 时间
    
    # 内存使用情况
    memory_percent = db.Column(db.Float, nullable=False)  # 内存使用率
    memory_rss = db.Column(db.BigInteger, nullable=False)  # 物理内存使用量
    memory_vms = db.Column(db.BigInteger, nullable=False)  # 虚拟内存使用量
    
    # 进程状态
    status = db.Column(db.String(20), nullable=False)  # 进程状态
    create_time = db.Column(db.DateTime, nullable=False)  # 创建时间
    num_threads = db.Column(db.Integer, nullable=False)  # 线程数
    num_fds = db.Column(db.Integer, nullable=True)  # 文件描述符数量

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'pid': self.pid,
            'name': self.name,
            'cpu': {
                'percent': self.cpu_percent,
                'times_user': self.cpu_times_user,
                'times_system': self.cpu_times_system
            },
            'memory': {
                'percent': self.memory_percent,
                'rss': self.memory_rss,
                'vms': self.memory_vms
            },
            'status': {
                'state': self.status,
                'create_time': self.create_time.isoformat(),
                'num_threads': self.num_threads,
                'num_fds': self.num_fds
            }
        }

class ActionLog(db.Model):
    __tablename__ = 'action_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    target = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    source_ip = db.Column(db.String(45), nullable=True)  # 来源 IP，支持 IPv6 地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 添加关系
    user = relationship('User', back_populates='action_logs')

    def __repr__(self):
        return f"<ActionLog {self.action} by User {self.user_id}>"
    
    def __init__(self, user_id, action, target, details=None, source_ip=None):
        self.id = str(uuid.uuid4())  # 自动生成UUID
        self.user_id = user_id
        self.action = action
        self.target = target
        self.details = details
        self.source_ip = source_ip

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "target": self.target,
            "details": self.details,
            "source_ip": self.source_ip,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ScanSubnet(db.Model):
    __tablename__ = 'scan_subnets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False) # 网段名称
    subnet = db.Column(db.String(32), nullable=False)  # 网段地址
    deleted = db.Column(db.Boolean, default=False, nullable=False)  # 软删除标志
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # 添加关系
    user = relationship('User', back_populates='scan_subnets')
    jobs = relationship('ScanJob', back_populates='subnet', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<ScanSubnet {self.subnet} by User {self.user_id}>"

    def __init__(self, user_id, name, subnet):
        self.id = str(uuid.uuid4())
        self.name = name
        self.user_id = user_id
        self.subnet = subnet
        self.deleted = False
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "subnet": self.subnet,
            "deleted": self.deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        }

class ScanPolicy(db.Model):
    __tablename__ = 'scan_policies'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    strategies = db.Column(db.Text)  # JSON string of strategies
    threads = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='active')  # active, running, completed, failed
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    
    # 添加关联关系
    user = relationship('User', back_populates='scan_policies')
    jobs = relationship('ScanJob', back_populates='policy', cascade='all, delete-orphan')
    subnets = relationship('ScanSubnet', 
                           secondary='policy_subnet_association',
                           backref=db.backref('policies', lazy='dynamic'),
                           lazy='dynamic')

    def __repr__(self):
        return f"<ScanPolicy {self.name}>"

    def __init__(self, name, user_id, description, threads, strategies):
        self.id = str(uuid.uuid4())
        self.name = name
        self.user_id = user_id
        self.description = description
        self.threads = threads
        self.strategies = json.dumps(strategies)  # 存储为 JSON 字符串
        self.status = 'active'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            "threads": self.threads,
            "strategies": json.loads(self.strategies),  # 解析 JSON 字符串
            "status": self.status,
            "deleted": self.deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ScanJob(db.Model):
    __tablename__ = 'scan_jobs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    policy_id = db.Column(db.String(36), db.ForeignKey('scan_policies.id'), nullable=False)
    subnet_id = db.Column(db.String(36), db.ForeignKey('scan_subnets.id'), nullable=False)
    status = db.Column(db.String(36), default='pending', nullable=False)
    progress = db.Column(db.Integer, default=0, nullable=False)  # 扫描进度百分比
    machines_found = db.Column(db.Integer, default=0, nullable=False)  # 发现的机器数量
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.String(255), nullable=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # 关系
    user = relationship('User', back_populates='scan_jobs')
    policy = relationship('ScanPolicy', back_populates='jobs')
    subnet = relationship('ScanSubnet', back_populates='jobs')
    scan_results = relationship('ScanResult', back_populates='job', lazy='dynamic')

    def __repr__(self):
        return f"<ScanJob {self.id} on Subnet {self.subnet_id}>"

    def __init__(self, user_id, subnet_id, policy_id, status='pending', progress=0, start_time=None, end_time=None, machines_found=0, error_message=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.subnet_id = subnet_id
        self.policy_id = policy_id
        self.status = status
        self.progress = progress
        self.start_time = start_time
        self.end_time = end_time
        self.machines_found = machines_found
        self.error_message = error_message
        self.deleted = False

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subnet_id": self.subnet_id,
            "policy": {
                "id": self.policy.id,
                "name": self.policy.name,
                "description": self.policy.description,
                "strategies": json.loads(self.policy.strategies) if isinstance(self.policy.strategies, str) else self.policy.strategies,
                "status": self.policy.status,
                "created_at": self.policy.created_at.isoformat() if self.policy.created_at else None,
                "updated_at": self.policy.updated_at.isoformat() if self.policy.updated_at else None
            } if self.policy else None,
            "subnet": {
                "id": self.subnet.id,
                "name": self.subnet.name,
                "subnet": self.subnet.subnet,
            },
            "results": [result.to_dict() for result in self.scan_results],
            "status": self.status,
            "progress": self.progress,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "machines_found": self.machines_found,
            "error_message": self.error_message,
            "deleted": self.deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

class ScanResult(db.Model):
    """扫描结果模型"""
    __tablename__ = 'scan_results'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey('scan_jobs.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # 支持 IPv6
    open_ports = db.Column(db.JSON)  # 存储开放端口信息，格式：{"80": {"protocol": "tcp", "service": "http", "version": "nginx/1.18.0"}, "443": {...}}
    os_info = db.Column(db.String(255))  # 操作系统信息
    status = db.Column(db.String(20))    # 主机状态：up/down
    raw_data = db.Column(db.JSON)        # 原始扫描数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime)

    # 关联关系
    job = db.relationship('ScanJob', back_populates='scan_results')

    def __init__(self, job_id, ip_address, open_ports=None, os_info=None, status=None, raw_data=None):
        self.job_id = job_id
        self.ip_address = ip_address
        self.open_ports = open_ports or {}
        self.os_info = os_info
        self.status = status
        self.raw_data = raw_data
        self.deleted = False

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'ip_address': self.ip_address,
            'open_ports': self.open_ports,
            'os_info': self.os_info,
            'status': self.status,
            'raw_data': self.raw_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 添加策略和子网的关联表
policy_subnet_association = db.Table('policy_subnet_association',
    db.Column('policy_id', db.String(36), db.ForeignKey('scan_policies.id'), primary_key=True),
    db.Column('subnet_id', db.String(36), db.ForeignKey('scan_subnets.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.JSON, nullable=False)
    description = db.Column(db.String(256))
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = db.relationship('User', backref=db.backref('system_configs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Notification(db.Model):
    """通知模型"""
    __tablename__ = 'notifications'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # scan, ip, policy
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)

    # 关联关系
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class NotificationTemplate(db.Model):
    """通知模板模型"""
    __tablename__ = 'notification_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False, unique=True)
    title_template = db.Column(db.String(255), nullable=False)
    content_template = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # scan, ip, policy
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'title_template': self.title_template,
            'content_template': self.content_template,
            'type': self.type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_template(cls, name):
        """获取模板"""
        return cls.query.filter_by(name=name, is_active=True).first()

    def render(self, **kwargs):
        """渲染模板"""
        try:
            title = self.title_template.format(**kwargs)
            content = self.content_template.format(**kwargs)
            return title, content
        except KeyError as e:
            raise ValueError(f"模板渲染失败，缺少参数: {str(e)}")
        except Exception as e:
            raise ValueError(f"模板渲染失败: {str(e)}") 

class Credential(db.Model):
    """凭证管理模型"""
    __tablename__ = 'credentials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    credential_type = db.Column(db.String(20), nullable=False)  # linux, windows, vmware
    username = db.Column(db.Text, nullable=True)  # 加密存储
    password = db.Column(db.Text, nullable=True)  # 加密存储
    private_key = db.Column(db.Text, nullable=True)  # SSH私钥，加密存储
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('credentials', lazy=True))
    host_bindings = db.relationship('HostCredentialBinding', back_populates='credential', cascade='all, delete-orphan')
    
    def to_dict(self, include_password=False):
        """转换为字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'credential_type': self.credential_type,
            'username': self.username,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        # 只有当明确要求时才返回密码
        if include_password:
            result['password'] = self.password
            result['private_key'] = self.private_key
        return result

class HostInfo(db.Model):
    """主机详细信息模型"""
    __tablename__ = 'host_infos'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_id = db.Column(db.String(36), db.ForeignKey('ips.id', ondelete='CASCADE'), nullable=False)
    scan_result_id = db.Column(db.String(36), db.ForeignKey('scan_results.id', ondelete='SET NULL'), nullable=True)
    parent_host_id = db.Column(db.String(36), db.ForeignKey('host_infos.id', ondelete='CASCADE'), nullable=True)  # 父主机ID，用于VMware树形结构
    host_type = db.Column(db.String(20), nullable=True)  # physical, vmware, other_virtualization
    hostname = db.Column(db.String(255))
    os_name = db.Column(db.String(255))
    os_version = db.Column(db.String(255))
    kernel_version = db.Column(db.String(255))
    cpu_model = db.Column(db.String(255))
    cpu_cores = db.Column(db.Integer)
    memory_total = db.Column(db.BigInteger)  # MB
    memory_free_mb = db.Column(db.Integer)  # 空闲内存（MB）
    disk_info = db.Column(db.JSON)
    disk_count = db.Column(db.Integer)  # 磁盘数量（计算字段）
    disk_total_gb = db.Column(db.Float)  # 总磁盘容量（GB，计算字段）
    network_interfaces = db.Column(db.JSON)
    network_count = db.Column(db.Integer)  # 网卡数量（计算字段）
    os_bit = db.Column(db.String(10))  # 操作系统位数（32-bit, 64-bit）
    boot_method = db.Column(db.String(20))  # 启动方式（BIOS, UEFI）
    vmware_info = db.Column(db.JSON)
    collection_status = db.Column(db.String(20), default='pending')  # pending, collecting, success, failed
    collection_error = db.Column(db.Text)
    last_collected_at = db.Column(db.DateTime)
    raw_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    
    # 关联关系
    ip = db.relationship('IP', backref=db.backref('host_info', uselist=False))
    scan_result = db.relationship('ScanResult', backref=db.backref('host_info', uselist=False))
    credential_bindings = db.relationship('HostCredentialBinding', back_populates='host', cascade='all, delete-orphan')
    parent_host = db.relationship('HostInfo', remote_side=[id], backref='child_hosts')
    
    def to_dict(self, include_children=False):
        """转换为字典"""
        result = {
            'id': self.id,
            'ip_id': self.ip_id,
            'scan_result_id': self.scan_result_id,
            'parent_host_id': self.parent_host_id,
            'host_type': self.host_type,
            'hostname': self.hostname,
            'os_name': self.os_name,
            'os_version': self.os_version,
            'kernel_version': self.kernel_version,
            'cpu_model': self.cpu_model,
            'cpu_cores': self.cpu_cores,
            'memory_total': self.memory_total,
            'memory_free_mb': self.memory_free_mb,
            'disk_info': self.disk_info,
            'disk_count': self.disk_count,
            'disk_total_gb': self.disk_total_gb,
            'network_interfaces': self.network_interfaces,
            'network_count': self.network_count,
            'os_bit': self.os_bit,
            'boot_method': self.boot_method,
            'vmware_info': self.vmware_info,
            'collection_status': self.collection_status,
            'collection_error': self.collection_error,
            'last_collected_at': self.last_collected_at.isoformat() if self.last_collected_at else None,
            'raw_data': self.raw_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ip': self.ip.to_dict() if self.ip else None
        }
        
        # 如果需要包含子主机（用于树形结构）
        if include_children:
            result['child_hosts'] = [child.to_dict(include_children=True) for child in self.child_hosts if not child.deleted]
        
        return result

class HostCredentialBinding(db.Model):
    """主机凭证绑定关系模型"""
    __tablename__ = 'host_credential_bindings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    host_id = db.Column(db.String(36), db.ForeignKey('host_infos.id', ondelete='CASCADE'), nullable=False)
    credential_id = db.Column(db.String(36), db.ForeignKey('credentials.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    host = db.relationship('HostInfo', back_populates='credential_bindings')
    credential = db.relationship('Credential', back_populates='host_bindings')
    
    # 唯一约束：一个主机只能绑定一个特定凭证
    __table_args__ = (
        db.UniqueConstraint('host_id', 'credential_id', name='unique_host_credential'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'host_id': self.host_id,
            'credential_id': self.credential_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'credential': self.credential.to_dict() if self.credential else None
        }

class CollectionTask(db.Model):
    """采集任务模型"""
    __tablename__ = 'collection_tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    trigger_type = db.Column(db.String(20), nullable=False)  # auto, manual
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    total_hosts = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('collection_tasks', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trigger_type': self.trigger_type,
            'status': self.status,
            'total_hosts': self.total_hosts,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


class CollectionProgress(db.Model):
    """采集进度追踪模型"""
    __tablename__ = 'collection_progress'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(36), nullable=False, index=True)  # 关联CollectionTask的ID
    host_id = db.Column(db.String(36), db.ForeignKey('host_infos.id', ondelete='SET NULL'), nullable=True)  # 当前处理的主机ID（可选）
    total_count = db.Column(db.Integer, default=0)  # 总任务数
    completed_count = db.Column(db.Integer, default=0)  # 已完成数
    failed_count = db.Column(db.Integer, default=0)  # 失败数
    current_step = db.Column(db.String(255))  # 当前步骤描述
    status = db.Column(db.String(20), default='running')  # running, completed, failed, cancelled
    error_message = db.Column(db.Text)  # 错误信息（如果有）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    host = db.relationship('HostInfo', backref=db.backref('collection_progress_records', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        progress_percent = 0
        if self.total_count > 0:
            # 计算进度百分比：已完成数 + 失败数 / 总数
            total_completed = self.completed_count + self.failed_count
            progress_percent = round((total_completed / self.total_count) * 100, 2)
            # 确保进度不超过100%
            if progress_percent > 100:
                progress_percent = 100.0
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'host_id': self.host_id,
            'total_count': self.total_count,
            'completed_count': self.completed_count,
            'failed_count': self.failed_count,
            'current_step': self.current_step,
            'status': self.status,
            'error_message': self.error_message,
            'progress_percent': progress_percent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_progress(self, completed=None, failed=None, current_step=None, status=None, error_message=None, commit=False):
        """
        更新进度
        
        Args:
            completed: 已完成数量
            failed: 失败数量
            current_step: 当前步骤描述
            status: 状态
            error_message: 错误信息
            commit: 是否自动提交（默认False，由调用者控制事务）
        """
        if completed is not None:
            self.completed_count = completed
        if failed is not None:
            self.failed_count = failed
        if current_step is not None:
            self.current_step = current_step
        if status is not None:
            self.status = status
        if error_message is not None:
            self.error_message = error_message
        self.updated_at = datetime.utcnow()
        if commit:
            db.session.commit() 