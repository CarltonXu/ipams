from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import pytz
from app.models.models import db, ScanPolicy, ScanJob, ScanSubnet
from app.tasks.task_manager import TaskManager
import json
import logging
import shutil
import threading
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyScheduler:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _running_jobs = set()
    _scheduler_started = False
    _scheduler = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PolicyScheduler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    if PolicyScheduler._scheduler is None:
                        PolicyScheduler._scheduler = BackgroundScheduler()
                    self.scheduler = PolicyScheduler._scheduler
                    self.task_manager = TaskManager()
                    self.app = None
                    self._initialized = True
                    logger.info("PolicyScheduler initialized")
        
    def init_app(self, app):
        """初始化应用实例"""
        if not self.app:
            self.app = app
            if not self._scheduler_started and not self.scheduler.running:
                self.scheduler.start()
                self._scheduler_started = True
                logger.info("Scheduler started")
                # 在启动调度器后立即初始化任务
                self.init_scheduler()
    
    def init_scheduler(self):
        """初始化调度器，加载所有活动的策略"""
        if not self.app:
            logger.error("Application not initialized")
            return
            
        try:
            with self._lock:
                # 检查是否已经在运行
                existing_jobs = self.scheduler.get_jobs()
                if existing_jobs:
                    logger.info(f"Scheduler already has {len(existing_jobs)} jobs, skipping initialization")
                    return
                    
                with self.app.app_context():
                    # 获取所有活动的策略
                    policies = ScanPolicy.query.filter_by(
                        deleted=False,
                        status='active'
                    ).all()
                    
                    for policy in policies:
                        self.schedule_policy(policy)
                        
                    logger.info(f"Initialized scheduler with {len(policies)} policies")
        except Exception as e:
            logger.error(f"Error initializing scheduler: {str(e)}")
    
    def schedule_policy(self, policy):
        """调度单个策略"""
        try:
            strategies = json.loads(policy.strategies)
            for strategy in strategies:
                # 创建定时任务
                job_id = f"{policy.id}_{strategy['cron']}"
                
                # 检查任务是否已存在
                if self.scheduler.get_job(job_id):
                    logger.warning(f"Job {job_id} already exists, skipping")
                    continue
                
                # 添加 cron 触发器
                self.scheduler.add_job(
                    self.execute_policy,
                    CronTrigger.from_crontab(strategy['cron']),
                    id=job_id,
                    args=[policy.id, strategy],
                    replace_existing=True,
                    coalesce=True,  # 如果错过了执行时间，只执行一次
                    misfire_grace_time=60  # 允许60秒的容错时间
                )
                
                # 如果开始时间在未来，添加一次性触发器
                start_time = datetime.fromisoformat(strategy['start_time'].replace('Z', '+00:00'))
                if start_time > datetime.now(pytz.UTC):
                    start_job_id = f"{job_id}_start"
                    if not self.scheduler.get_job(start_job_id):
                        self.scheduler.add_job(
                            self.execute_policy,
                            DateTrigger(run_date=start_time),
                            id=start_job_id,
                            args=[policy.id, strategy],
                            replace_existing=True,
                            coalesce=True,  # 如果错过了执行时间，只执行一次
                            misfire_grace_time=60  # 允许60秒的容错时间
                        )
                
                logger.info(f"Scheduled policy {policy.name} with cron {strategy['cron']}")
        except Exception as e:
            logger.error(f"Error scheduling policy {policy.id}: {str(e)}")
    
    def execute_policy(self, policy_id, strategy):
        """执行策略扫描"""
        if not self.app:
            logger.error("Application not initialized")
            return
            
        # 检查是否已经在执行相同的策略
        job_key = f"{policy_id}_{strategy.get('cron', '')}"
        if job_key in self._running_jobs:
            logger.warning(f"Policy {policy_id} is already running, skipping")
            return
            
        try:
            with self.app.app_context():
                policy = ScanPolicy.query.get(policy_id)
                if not policy or policy.deleted or policy.status != 'active':
                    return
                
                # 检查是否有正在运行的相同策略的任务
                running_jobs = ScanJob.query.filter_by(
                    policy_id=policy_id,
                    status='running'
                ).first()
                
                if running_jobs:
                    logger.warning(f"Policy {policy.name} has running jobs, skipping")
                    # 创建失败的任务记录，说明跳过原因
                    self._create_failed_job(policy, strategy, "Policy has running jobs, skipping execution")
                    return
                
                # 标记任务为运行中
                self._running_jobs.add(job_key)
                
                try:
                    # 检查 nmap 是否可用
                    if not shutil.which('nmap'):
                        error_msg = "nmap program not found in system path"
                        logger.error(error_msg)
                        # 创建失败的任务记录
                        self._create_failed_job(policy, strategy, error_msg)
                        return
                    
                    # 获取要扫描的子网
                    subnet_ids = strategy.get('subnet_ids', [])
                    scan_params = strategy.get('scan_params', {
                        'enable_custom_ports': False,
                        'ports': '',
                        'enable_custom_scan_type': False,
                        'scan_type': 'default'
                    })

                    if not subnet_ids:
                        # 如果没有指定子网，使用策略关联的所有子网
                        subnet_ids = [subnet.id for subnet in policy.subnets]
                    
                    # 为每个子网创建扫描任务
                    for subnet_id in subnet_ids:
                        subnet = ScanSubnet.query.get(subnet_id)
                        if not subnet or subnet.deleted:
                            continue
                        
                        try:
                            # 使用任务管理器执行扫描
                            self.task_manager.submit_scan_task(None, policy_id, subnet_id, scan_params)
                        except Exception as e:
                            error_msg = f"Failed to submit scan task for subnet {subnet_id}: {str(e)}"
                            logger.error(error_msg)
                            # 创建失败的任务记录
                            self._create_failed_job(policy, strategy, error_msg)
                            continue
                        
                    logger.info(f"Executed policy {policy.name} for subnets {subnet_ids}")
                finally:
                    # 移除运行标记
                    self._running_jobs.discard(job_key)
                    
        except Exception as e:
            logger.error(f"Error executing policy {policy_id}: {str(e)}")
            # 确保在发生异常时也移除运行标记
            self._running_jobs.discard(job_key)
            # 创建失败的任务记录
            with self.app.app_context():
                policy = ScanPolicy.query.get(policy_id)
                if policy:
                    self._create_failed_job(policy, strategy, str(e))
    
    def _create_failed_job(self, policy, strategy, error_msg):
        """创建失败的任务记录"""
        try:
            subnet_ids = strategy.get('subnet_ids', [])
            if not subnet_ids:
                subnet_ids = [subnet.id for subnet in policy.subnets]
            
            for subnet_id in subnet_ids:
                subnet = ScanSubnet.query.get(subnet_id)
                if not subnet or subnet.deleted:
                    continue
                
                job = ScanJob(
                    user_id=policy.user_id,
                    policy_id=policy.id,
                    subnet_id=subnet_id,
                    status='failed',
                    error_message=error_msg,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow()
                )
                db.session.add(job)
            
            db.session.commit()
            logger.info(f"Created failed job records for policy {policy.name}")
        except Exception as e:
            logger.error(f"Error creating failed job records: {str(e)}")
            db.session.rollback()
    
    def remove_policy(self, policy_id):
        """移除策略的调度任务"""
        if not self.app:
            logger.error("Application not initialized")
            return
            
        try:
            with self.app.app_context():
                policy = ScanPolicy.query.get(policy_id)
                if not policy:
                    return
                
                # 获取所有与这个策略相关的任务
                all_jobs = self.scheduler.get_jobs()
                policy_jobs = [job for job in all_jobs if job.id.startswith(f"{policy_id}_")]
                
                # 移除所有相关的任务
                for job in policy_jobs:
                    try:
                        self.scheduler.remove_job(job.id)
                        logger.info(f"Removed job {job.id}")
                    except Exception as e:
                        logger.warning(f"Failed to remove job {job.id}: {str(e)}")
                
                # 清除运行标记
                self._running_jobs = {job for job in self._running_jobs if not job.startswith(f"{policy_id}_")}
                
                logger.info(f"Removed all jobs for policy {policy.name}")
        except Exception as e:
            logger.error(f"Error removing policy {policy_id}: {str(e)}")
    
    def update_policy(self, policy_id):
        """更新策略的调度任务"""
        if not self.app:
            logger.error("Application not initialized")
            return
            
        try:
            with self.app.app_context():
                # 先移除旧的调度任务
                self.remove_policy(policy_id)
                # 添加新的调度任务
                policy = ScanPolicy.query.get(policy_id)
                if policy and not policy.deleted and policy.status == 'active':
                    self.schedule_policy(policy)
                
                logger.info(f"Updated policy {policy_id} in scheduler")
        except Exception as e:
            logger.error(f"Error updating policy {policy_id}: {str(e)}")

# 创建全局调度器实例
scheduler = PolicyScheduler() 