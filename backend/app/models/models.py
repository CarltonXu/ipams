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
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    subnet_ids = db.Column(db.String(500), nullable=False)
    strategies = db.Column(db.String(255) , nullable=False)  # 扫描策略
    status = db.Column(db.Enum('active', 'running', 'completed', 'failed', name='scan_status'), default='active', nullable=False)
    description = db.Column(db.String(255), nullable=False)  # 扫描策略描述
    start_time = db.Column(db.String(255), nullable=False)  # 扫描开始时间
    threads = db.Column(db.Integer, default=1, nullable=False)  # 并发线程数，默认1
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # 添加关系
    user = relationship('User', back_populates='scan_policies')
    jobs = relationship('ScanJob', back_populates='policy', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<ScanPolicy {self.strategies} on Subnet {self.subnet_ids}>"

    def __init__(self, name, user_id, subnet_ids, strategies, description, start_time, threads=1):
        self.id = str(uuid.uuid4())
        self.name = name
        self.user_id = user_id
        self.subnet_ids = json.dumps(subnet_ids)
        self.strategies = strategies
        self.status = 'active'
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
            "status": self.status,
            "deleted": self.deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
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
    results = relationship('ScanResult', back_populates='job', cascade='all, delete-orphan')

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
            "policy_id": self.policy_id,
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
    __tablename__ = 'scan_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey('scan_jobs.id'), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    open_ports = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    job = relationship('ScanJob', back_populates='results')

    def __init__(self, job_id, ip_address, open_ports):
        self.job_id = job_id
        self.ip_address = ip_address
        self.open_ports = open_ports

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "ip_address": self.ip_address,
            "open_ports": self.open_ports,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        }