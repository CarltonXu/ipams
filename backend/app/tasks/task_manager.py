from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import logging
import threading
from app.models.models import db, ScanJob, ScanSubnet, ScanPolicy
from .scan_executor import ScanExecutor
from .task_state import task_state
from flask import current_app

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
                
                # 获取子网信息
                subnet = ScanSubnet.query.get(subnet_id)
                if not subnet:
                    logger.error(f"Subnet {subnet_id} not found")
                    raise ValueError(f"Subnet {subnet_id} not found")
                
                # 获取策略信息
                policy = ScanPolicy.query.get(policy_id)
                if not policy:
                    logger.error(f"Policy {policy_id} not found")
                    raise ValueError(f"Policy {policy_id} not found")
                
                # 创建扫描执行器
                executor = ScanExecutor(
                    job_id=job_id,
                    subnet=subnet.subnet,
                    threads=policy.threads
                )
            
            # 提交任务到线程池
            future = self.executor.submit(
                self._execute_scan_task,
                app,
                job_id,
                policy_id,
                subnet_id,
                executor  # 传递执行器实例
            )
            
            # 创建任务记录，保存 future 对象和执行器实例
            task_state.create_task(job_id, policy_id, subnet_id, future, executor)
            
            # 设置回调
            future.add_done_callback(
                lambda f: self._update_job_status(job_id, f)
            )
            
            logger.info(f"Task {job_id} submitted successfully")
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
            
            # 清理任务资源
            task = task_state.get_task(job_id)
            if task and task.get('executor'):
                try:
                    task['executor'].cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up task {job_id}: {str(e)}")
            
            # 移除任务记录
            task_state.remove_task(job_id)
            
        except Exception as e:
            logger.error(f"Failed to update job status for {job_id}: {str(e)}")
            task_state.update_task_status(job_id, 'failed', str(e))

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
            
            # 获取任务相关的 future
            future = task.get('future')
            if future:
                # 尝试取消任务
                cancelled = future.cancel()
                
                # 即使 future 取消失败，也尝试停止扫描执行器
                executor = task.get('executor')
                if executor and hasattr(executor, 'cancel'):
                    executor.cancel()
                    logger.info(f"Scan executor for task {job_id} cancelled")
                    
                    # 更新任务状态为已取消
                    task_state.update_task_status(job_id, 'cancelled')
                    logger.info(f"Task {job_id} marked as cancelled")
                    return True
                else:
                    logger.warning(f"No executor found for task {job_id}")
                    return False
            else:
                logger.warning(f"No future found for task {job_id}")
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
            if hasattr(self, 'executor'):
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
                self.executor.shutdown(wait=False, cancel_futures=True)
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
                if hasattr(self, 'executor'):
                    self.executor.shutdown(wait=False, cancel_futures=True)
                task_state._tasks.clear()
                self._initialized = False
                self._instance = None
            except Exception as cleanup_error:
                logger.error(f"Error during forced cleanup: {str(cleanup_error)}")

# 创建全局任务管理器实例
task_manager = TaskManager()

def init_app(app):
    """初始化应用"""
    @app.before_first_request
    def initialize():
        """在第一个请求之前初始化"""
        logger.info("Initializing TaskManager")
        # 确保 TaskManager 被初始化
        task_manager

    @app.teardown_appcontext
    def cleanup(exception=None):
        """在应用上下文结束时清理"""
        if exception:
            logger.error(f"Error during request: {str(exception)}")
        logger.info("Cleaning up TaskManager")
        task_manager.shutdown() 