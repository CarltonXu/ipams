import threading
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.utils.logger import app_logger as logger

class TaskState:
    def __init__(self):
        self._tasks = {}
        self._lock = threading.Lock()

    def create_task(self, job_id: str, policy_id: str, subnet_id: str, future=None, executor=None):
        """创建任务记录"""
        with self._lock:
            self._tasks[job_id] = {
                'status': 'pending',
                'progress': 0,
                'machines_found': 0,
                'policy_id': policy_id,
                'subnet_id': subnet_id,
                'future': future,
                'executor': executor,
                'error': None
            }
            logger.info(f"Created task {job_id}")

    def update_task_status(self, job_id: str, status: str, error: str = None):
        """更新任务状态"""
        with self._lock:
            if job_id in self._tasks:
                self._tasks[job_id]['status'] = status
                if error:
                    self._tasks[job_id]['error'] = error
                if status in ['completed', 'failed', 'cancelled']:
                    self._tasks[job_id]['end_time'] = datetime.utcnow()
                logger.info(f"Updated task {job_id} status to {status}")

    def update_task_progress(self, job_id: str, progress: float, machines_found: int = 0):
        """更新任务进度"""
        with self._lock:
            if job_id in self._tasks:
                self._tasks[job_id]['progress'] = progress
                self._tasks[job_id]['machines_found'] = machines_found
                logger.debug(f"Updated task {job_id} progress to {progress}%")

    def get_task(self, job_id: str) -> dict:
        """获取任务状态"""
        with self._lock:
            return self._tasks.get(job_id, {
                'name': None,
                'status': 'not_found',
                'progress': 0,
                'machines_found': 0,
                'error': None
            })

    def remove_task(self, job_id: str):
        """移除任务记录"""
        with self._lock:
            if job_id in self._tasks:
                del self._tasks[job_id]
                logger.info(f"Removed task {job_id}")

# 创建全局任务状态管理器实例
task_state = TaskState()