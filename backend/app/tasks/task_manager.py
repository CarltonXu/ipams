from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import logging
import threading
import os
import multiprocessing
from app.models.models import db, ScanJob, ScanSubnet, ScanPolicy
from app.services.scan.executor import ScanExecutor
from app.tasks.task_state import task_state
from app.core.utils.logger import app_logger as logger
from flask import current_app
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskManager:
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    # 根据系统CPU核心数动态设置线程池大小
                    cpu_count = multiprocessing.cpu_count()
                    max_workers = min(cpu_count * 2, 20)  # 最多20个线程
                    
                    # 从环境变量获取线程池大小
                    env_workers = os.getenv('TASK_MANAGER_WORKERS')
                    if env_workers:
                        try:
                            max_workers = min(int(env_workers), 50)  # 最多50个线程
                        except ValueError:
                            logger.warning(f"Invalid TASK_MANAGER_WORKERS value: {env_workers}")
                    
                    self._executor = ThreadPoolExecutor(
                        max_workers=max_workers,
                        thread_name_prefix='scan_worker'
                    )
                    self._futures = {}
                    self._initialized = True
                    logger.info(f"TaskManager initialized with ThreadPoolExecutor (max_workers={max_workers})")

    def init_app(self, app):
        """初始化应用实例"""
        self.app = app
        logger.info("TaskManager app initialized")

    def submit_scan_task(self, job_id: str, policy_id: str, subnet_id: str, scan_params: dict = None) -> ScanJob:
        """提交扫描任务"""
        try:
            # 检查 nmap 是否可用
            if not shutil.which('nmap'):
                raise RuntimeError("nmap program not found in system path")
                
            # 获取当前应用实例
            app = current_app._get_current_object()
            
            with app.app_context():
                # 获取策略信息
                policy = ScanPolicy.query.get(policy_id)
                if not policy:
                    logger.error(f"Policy {policy_id} not found in database")
                    raise ValueError(f"Policy {policy_id} not found in database")
                
                # 获取子网信息
                subnet = ScanSubnet.query.get(subnet_id)
                if not subnet:
                    logger.error(f"Subnet {subnet_id} not found")
                    raise ValueError(f"Subnet {subnet_id} not found")
                
                # 创建扫描任务记录
                job = ScanJob(
                    user_id=policy.user_id,
                    policy_id=policy_id,
                    subnet_id=subnet_id,
                    status='pending',
                    start_time=datetime.utcnow()
                )
                db.session.add(job)
                db.session.commit()
                
                # 检查任务是否已存在
                existing_task = task_state.get_task(job.id)
                if existing_task['status'] != 'not_found' and existing_task['status'] not in ['failed', 'cancelled']:
                    logger.warning(f"Task {job.id} already exists with status {existing_task['status']}")
                    return job
                
                # 创建扫描执行器
                executor = ScanExecutor(
                    job_id=job.id,
                    subnet=subnet.subnet,
                    threads=policy.threads,
                    scan_params=scan_params  # 传递扫描参数
                )
            
            # 提交任务到线程池
            future = self._executor.submit(
                self._execute_scan_task,
                app,
                job.id,
                policy_id,
                subnet_id,
                executor  # 传递执行器实例
            )
            
            # 创建任务记录，保存 future 对象和执行器实例
            task_state.create_task(job.id, policy_id, subnet_id, future, executor)
            
            # 设置回调
            future.add_done_callback(
                lambda f: self._update_job_status(job.id, f)
            )
            
            logger.info(f"Task {job.id} submitted successfully")
            return job
        except Exception as e:
            logger.error(f"Failed to submit task {job_id}: {str(e)}")
            task_state.update_task_status(job_id, 'failed', str(e))
            raise

    def _execute_scan_task(self, app, job_id: str, policy_id: str, subnet_id: str, executor: ScanExecutor) -> Dict[str, Any]:
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
                
                # 执行扫描
                success = executor.execute()
                
                if success:
                    task_state.update_task_status(job_id, 'completed')
                    return {'status': 'completed'}
                else:
                    task_state.update_task_status(job_id, 'failed', 'Scan execution failed')
                    return {'status': 'failed', 'error': 'Scan execution failed'}
                    
            except Exception as e:
                logger.error(f"Error executing scan task {job_id}: {str(e)}")
                task_state.update_task_status(job_id, 'failed', str(e))
                return {'status': 'failed', 'error': str(e)}

    def _update_job_status(self, job_id: str, future) -> None:
        """更新任务状态"""
        try:
            result = future.result()
            with current_app.app_context():
                job = ScanJob.query.get(job_id)
                if job:
                    job.status = result['status']
                    if result.get('error'):
                        job.error_message = result['error']
                    job.end_time = datetime.utcnow()
                    db.session.commit()
                    logger.info(f"Updated task {job_id} status to {result['status']}")
                else:
                    logger.error(f"Job {job_id} not found")
        except Exception as e:
            logger.error(f"Error updating job status {job_id}: {str(e)}")

    def get_task_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return task_state.get_task(job_id)

    def cancel_task(self, job_id: str) -> bool:
        """取消任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            bool: 是否成功取消任务
        """
        try:
            # 获取任务状态
            task = task_state.get_task(job_id)
            if task['status'] == 'not_found':
                logger.error(f"Task {job_id} not found")
                return False
                
            if task['status'] not in ['pending', 'running']:
                logger.warning(f"Cannot cancel task {job_id} with status {task['status']}")
                return False
            
            # 先尝试停止扫描执行器
            executor = task.get('executor')
            if executor and hasattr(executor, 'cancel'):
                # 强制停止执行器
                executor.cancel()
                logger.info(f"Scan executor for task {job_id} cancelled")
                
                # 更新任务状态为已取消
                task_state.update_task_status(job_id, 'cancelled')
                logger.info(f"Task {job_id} marked as cancelled")
                
                # 尝试取消 future
                future = task.get('future')
                if future:
                    if not future.done():
                        try:
                            # 尝试取消 future
                            cancelled = future.cancel()
                            if cancelled:
                                logger.info(f"Future for task {job_id} cancelled successfully")
                            else:
                                logger.warning(f"Failed to cancel future for task {job_id}")
                                # 如果 future 取消失败，尝试强制停止
                                if hasattr(future, '_thread'):
                                    import ctypes
                                    try:
                                        thread_id = future._thread.ident
                                        if thread_id:
                                            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                                                ctypes.c_long(thread_id),
                                                ctypes.py_object(SystemExit)
                                            )
                                            if res == 0:
                                                logger.warning(f"Failed to force stop thread for task {job_id}")
                                            elif res != 1:
                                                logger.warning(f"Failed to force stop thread for task {job_id}, res={res}")
                                    except Exception as e:
                                        logger.error(f"Error force stopping thread for task {job_id}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error cancelling future for task {job_id}: {str(e)}")
                    else:
                        logger.info(f"Future for task {job_id} already done")
                
                # 清理任务状态
                try:
                    task_state.remove_task(job_id)
                    logger.info(f"Task {job_id} removed from task state")
                except Exception as e:
                    logger.error(f"Error removing task {job_id} from task state: {str(e)}")
                
                return True
            else:
                logger.warning(f"No executor found for task {job_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling task {job_id}: {str(e)}")
            return False

    def update_task_progress(self, job_id: str, progress: float, machines_found: int = 0) -> None:
        """更新任务进度"""
        task_state.update_task_progress(job_id, progress, machines_found)

    def shutdown(self) -> None:
        """关闭任务管理器"""
        try:
            if hasattr(self, '_executor'):
                logger.info("Shutting down TaskManager...")
                
                # 取消所有正在运行的任务
                for job_id, task in list(task_state._tasks.items()):
                    try:
                        # 取消 future
                        future = task.get('future')
                        if future and not future.done():
                            future.cancel()
                            logger.info(f"Cancelled future for task {job_id}")
                        
                        # 清理执行器
                        executor = task.get('executor')
                        if executor:
                            executor.cleanup()
                            logger.info(f"Cleaned up executor for task {job_id}")
                    except Exception as e:
                        logger.error(f"Error cleaning up task {job_id}: {str(e)}")
                
                # 关闭线程池，设置超时时间
                logger.info("Shutting down thread pool...")
                self._executor.shutdown(wait=False, cancel_futures=True)
                logger.info("Thread pool shutdown completed")
                
                # 清理任务状态
                task_state._tasks.clear()
                logger.info("Task state cleared")
                
                # 重置初始化标志
                self._initialized = False
                self._instance = None
                
                logger.info("TaskManager shutdown completed")
        except Exception as e:
            logger.error(f"Error during TaskManager shutdown: {str(e)}")
            # 强制清理
            try:
                if hasattr(self, '_executor'):
                    self._executor.shutdown(wait=False, cancel_futures=True)
                task_state._tasks.clear()
                self._initialized = False
                self._instance = None
            except Exception as cleanup_error:
                logger.error(f"Error during forced cleanup: {str(cleanup_error)}")

    def update_job_status(self, job_id: str, status: str, result: Optional[Dict] = None) -> None:
        """更新任务状态"""
        try:
            if not self.app:
                self.app = current_app._get_current_object()
            
            with self.app.app_context():
                job = ScanJob.query.get(job_id)
                if job:
                    job.status = status
                    if result:
                        job.result = result
                    db.session.commit()
                    logger.info(f"Updated task {job_id} status to {status}")
                else:
                    logger.error(f"Job {job_id} not found")
        except Exception as e:
            logger.error(f"Error updating job status {job_id}: {str(e)}")
            raise

# 创建全局任务管理器实例
task_manager = TaskManager()