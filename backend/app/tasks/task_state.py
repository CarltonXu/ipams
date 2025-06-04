from typing import Dict, Any, Optional
import threading
from datetime import datetime

class TaskState:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskState, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        self.tasks: Dict[str, Any] = {}
        self._task_lock = threading.Lock()
    
    def create_task(self, job_id: str, policy_id: str, subnet_id: str) -> None:
        """添加新任务"""
        with self._task_lock:
            self.tasks[job_id] = {
                'policy_id': policy_id,
                'subnet_id': subnet_id,
                'status': 'pending',
                'start_time': datetime.utcnow(),
                'progress': 0,
                'error_message': None
            }
    
    def update_task_status(self, job_id: str, status: str, error_message: Optional[str] = None) -> None:
        """更新任务状态"""
        with self._task_lock:
            if job_id in self.tasks:
                self.tasks[job_id]['status'] = status
                if error_message is not None:
                    self.tasks[job_id]['error_message'] = error_message
    
    def update_task_progress(self, job_id: str, progress: float, machines_found: int = 0) -> None:
        """更新任务进度"""
        with self._task_lock:
            if job_id in self.tasks:
                self.tasks[job_id]['progress'] = progress
                self.tasks[job_id]['machines_found'] = machines_found
    
    def get_task(self, job_id: str) -> Dict[str, Any]:
        """获取任务信息"""
        with self._task_lock:
            return self.tasks.get(job_id, {'status': 'not_found'})
    
    def remove_task(self, job_id: str) -> None:
        """移除任务"""
        with self._task_lock:
            self.tasks.pop(job_id, None)

# 创建全局任务状态实例
task_state = TaskState() 