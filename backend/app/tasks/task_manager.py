from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import logging
from ..models import db, ScanJob, ScanSubnet, ScanPolicy
from .scan_executor import ScanExecutor
from .task_state import task_state
from flask import current_app

logger = logging.getLogger(__name__)

class TaskManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.executor = ThreadPoolExecutor(max_workers=5)
            self._initialized = True
            logger.info("TaskManager initialized with ThreadPoolExecutor")

    def submit_scan_task(self, job_id: str, policy_id: str, subnet_id: str) -> None:
        """提交扫描任务到线程池"""
        try:
            # 获取当前应用实例
            app = current_app._get_current_object()
            
            with app.app_context():
                # 确保 Job 记录存在
                job = ScanJob.query.get(job_id)
                if not job:
                    logger.error(f"Job {job_id} not found in database")
                    raise ValueError(f"Job {job_id} not found in database")
                
                # 检查任务是否已存在
                existing_task = task_state.get_task(job_id)
                if existing_task['status'] != 'not_found' and existing_task['status'] not in ['failed', 'cancelled']:
                    logger.warning(f"Task {job_id} already exists with status {existing_task['status']}")
                    return
                
                # 创建任务记录
                task_state.create_task(job_id, policy_id, subnet_id)
            
            # 提交任务到线程池
            future = self.executor.submit(
                self._execute_scan_task,
                app,
                job_id,
                policy_id,
                subnet_id
            )
            
            # 设置回调
            future.add_done_callback(
                lambda f: self._update_job_status(job_id, f)
            )
            
            logger.info(f"Task {job_id} submitted successfully")
        except Exception as e:
            logger.error(f"Failed to submit task {job_id}: {str(e)}")
            task_state.update_task_status(job_id, 'failed', str(e))
            raise

    def _execute_scan_task(self, app, job_id: str, policy_id: str, subnet_id: str) -> Dict[str, Any]:
        """执行扫描任务"""
        with app.app_context():
            try:
                # 获取任务相关数据
                job = ScanJob.query.get(job_id)
                if not job:
                    logger.error(f"Job {job_id} not found")
                    return {'status': 'failed', 'error': 'Job not found'}
                
                subnet = ScanSubnet.query.get(subnet_id)
                if not subnet:
                    logger.error(f"Subnet {subnet_id} not found")
                    return {'status': 'failed', 'error': 'Subnet not found'}
                
                policy = ScanPolicy.query.get(policy_id)
                if not policy:
                    logger.error(f"Policy {policy_id} not found")
                    return {'status': 'failed', 'error': 'Policy not found'}
                
                # 更新任务状态为运行中
                task_state.update_task_status(job_id, 'running')
                logger.info(f"Starting scan for job {job_id}, subnet {subnet.subnet}")
                
                # 创建扫描任务
                executor = ScanExecutor(
                    job_id=job_id,
                    subnet=subnet.subnet,
                    threads=policy.threads
                )

                # 执行扫描
                success = executor.execute()
                
                if success:
                    # 更新任务状态为完成
                    task_state.update_task_status(job_id, 'completed')
                    logger.info(f"Task {job_id} completed successfully")
                    return {'status': 'completed'}
                else:
                    # 更新任务状态为失败
                    task_state.update_task_status(job_id, 'failed', 'Scan execution failed')
                    logger.error(f"Task {job_id} failed: Scan execution failed")
                    return {'status': 'failed', 'error': 'Scan execution failed'}
                    
            except Exception as e:
                logger.error(f"Task {job_id} failed: {str(e)}")
                task_state.update_task_status(job_id, 'failed', str(e))
                return {'status': 'failed', 'error': str(e)}

    def _update_job_status(self, job_id: str, future) -> None:
        """更新任务状态"""
        try:
            if future.cancelled():
                logger.info(f"Task {job_id} was cancelled")
                task_state.update_task_status(job_id, 'cancelled')
            elif future.exception():
                error = str(future.exception())
                logger.error(f"Task {job_id} failed with exception: {error}")
                task_state.update_task_status(job_id, 'failed', error)
            else:
                result = future.result()
                if result and result.get('status') == 'failed':
                    logger.error(f"Task {job_id} failed: {result.get('error')}")
                    task_state.update_task_status(job_id, 'failed', result.get('error'))
        except Exception as e:
            logger.error(f"Failed to update job status for {job_id}: {str(e)}")
            task_state.update_task_status(job_id, 'failed', str(e))

    def get_task_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return task_state.get_task(job_id)

    def update_task_progress(self, job_id: str, progress: float, machines_found: int = 0) -> None:
        """更新任务进度"""
        task_state.update_task_progress(job_id, progress, machines_found)

    def shutdown(self) -> None:
        """关闭任务管理器"""
        try:
            if hasattr(self, 'executor'):
                logger.info("Shutting down TaskManager...")
                self.executor.shutdown(wait=True)
                logger.info("TaskManager shutdown completed")
        except Exception as e:
            logger.error(f"Error during TaskManager shutdown: {str(e)}")
            raise

# 创建全局任务管理器实例
task_manager = TaskManager() 