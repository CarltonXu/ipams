from flask_sqlalchemy import SQLAlchemy
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
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(100))
    wechat_id = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)

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

class ActionLog(db.Model):
    __tablename__ = 'action_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    target = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    source_ip = db.Column(db.String(45), nullable=True)  # 来源 IP，支持 IPv6 地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

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
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    subnet_ids = db.Column(db.String(500), nullable=False)
    strategies = db.Column(db.String(255) , nullable=False)  # 扫描策略
    description = db.Column(db.String(255), nullable=False)  # 扫描策略描述
    start_time = db.Column(db.String(255), nullable=False)  # 扫描开始时间
    threads = db.Column(db.Integer, default=1, nullable=False)  # 并发线程数，默认1
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<ScanPolicy {self.strategies} on Subnet {self.subnet_ids}>"

    def __init__(self, name, user_id, subnet_ids, strategies, description, start_time, threads=1):
        self.id = str(uuid.uuid4())
        self.name = name
        self.user_id = user_id
        self.subnet_ids = json.dumps(subnet_ids)
        self.strategies = strategies
        self.description = description
        self.start_time = start_time
        self.threads = threads
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "subnet_ids": json.loads(self.subnet_ids),
            "strategies": self.strategies,
            "description": self.description,
            "start_time": self.start_time,
            "threads": self.threads,
            "deleted": self.deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        }


class ScanJob(db.Model):
    __tablename__ = 'scan_jobs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    subnet_id = db.Column(db.String(36), db.ForeignKey('scan_subnets.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed', name='scan_status'), default='pending', nullable=False)
    progress = db.Column(db.Integer, default=0, nullable=False)  # 扫描进度百分比
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    machines_found = db.Column(db.Integer, default=0, nullable=False)  # 发现的机器数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<ScanJob {self.id} on Subnet {self.subnet_id}>"

    def __init__(self, user_id, subnet_id, status='pending', start_time=None, end_time=None, machines_found=0):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.subnet_id = subnet_id
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.machines_found = machines_found
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subnet_id": self.subnet_id,
            "status": self.status,
            "progress": self.progress,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "machines_found": self.machines_found,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
