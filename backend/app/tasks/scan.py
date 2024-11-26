import time
import random
from models import db, ScanJob
from datetime import datetime

def perform_scan(job_id, subnet, threads):
    job = ScanJob.query.get(job_id)
    if not job:
        return

    job.status = 'running'
    job.start_time = datetime.utcnow()
    db.session.commit()

    # 模拟扫描逻辑
    for i in range(1, 101):  # 模拟进度
        time.sleep(random.uniform(0.01, 0.1))  # 模拟扫描耗时
        job.progress = i
        db.session.commit()

    job.status = 'completed'
    job.end_time = datetime.utcnow()
    job.machines_found = random.randint(1, 50)  # 模拟找到的机器数量
    db.session.commit()