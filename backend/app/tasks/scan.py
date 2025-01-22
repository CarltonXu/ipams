from ..celery.celery_app import celery
from ..models import db, ScanJob, ScanSubnet, ScanPolicy
from .scan_executor import ScanExecutor
from datetime import datetime
from flask import current_app

@celery.task(bind=True)
def execute_scan_task(self, job_id: str, policy_id: str, subnet_id: str):
    """执行扫描任务"""
    try:
        # 获取 Flask 应用实例
        app = current_app._get_current_object()
        
        with app.app_context():
            job = ScanJob.query.get(job_id)
            if not job:
                return
                
            subnet = ScanSubnet.query.get(subnet_id)
            if not subnet:
                job.status = 'failed'
                policy.status = 'failed'
                job.error_message = '网段不存在'
                db.session.commit()
                return
                
            policy = ScanPolicy.query.get(policy_id)
            if not policy:
                job.status = 'failed'
                policy.status = 'failed'
                job.error_message = '策略不存在'
                db.session.commit()
                return
                
            job.status = 'running'
            policy.status = 'running'
            job.start_time = datetime.utcnow()
            db.session.commit()
            
            # 更新任务状态
            self.update_state(state='PROGRESS', meta={'progress': 0})
            
            executor = ScanExecutor(
                job_id=job_id,
                subnet=subnet.subnet,
                threads=policy.threads,
                app=app  # 传入应用实例
            )
            
            success = executor.execute()
            
            job.status = 'completed' if success else 'failed'
            policy.status = 'completed' if success else 'failed'
            job.end_time = datetime.utcnow()
            if not success:
                job.error_message = '扫描执行失败'
            db.session.commit()
            
            return {'status': job.status, 'job_id': job_id}
            
    except Exception as e:
        if job:
            job.status = 'failed'
            policy.status = 'failed'
            job.error_message = str(e)
            job.end_time = datetime.utcnow()
            db.session.commit()
        raise