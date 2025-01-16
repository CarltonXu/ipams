import nmap
import threading
import time
from datetime import datetime
from celery.utils.log import get_task_logger
from ..models import db, ScanJob, ScanResult, IP

logger = get_task_logger(__name__)

class ScanExecutor:
    def __init__(self, job_id: str, subnet: str, threads: int = 10, app=None):
        self.job_id = job_id
        self.subnet = subnet
        self.threads = threads
        self.lock = threading.Lock()
        self.machines_found = 0
        self.nm = nmap.PortScanner()
        self.scanning = False
        self.current_phase = "discovery"
        self.app = app
        logger.info(f"Initializing scan executor for job {job_id} on subnet {subnet}")
        
    def monitor_progress(self):
        """监控扫描进度"""
        last_progress = -1
        
        while self.scanning:
            logger.info(f"Job {self.job_id} execute get_nmap_last_output: {self.nm.get_nmap_last_output()}")
            logger.info(f"Job {self.job_id} execute _nmap_last_output: {self.nm._nmap_last_output}")
            try:
                if self.current_phase == "discovery":
                    # 主机发现阶段，使用固定进度增长
                    current_progress = min(last_progress + 1, 30)
                else:
                    # 端口扫描阶段，根据已扫描主机数计算进度
                    if not hasattr(self, 'total_hosts') or self.total_hosts == 0:
                        current_progress = 30
                    else:
                        host_percentage = (self.scanned_hosts / self.total_hosts) * 70
                        current_progress = 30 + int(host_percentage)
                
                if current_progress != last_progress:
                    logger.info(f"Job {self.job_id}: {self.current_phase} progress: {current_progress}%")
                    self._update_progress(current_progress)
                    last_progress = current_progress
                    
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Progress monitoring error: {str(e)}")
        
    def _update_progress(self, progress: int):
        """更新扫描进度"""
        try:
            if not self.app:
                logger.error(f"Job {self.job_id}: No Flask app context available")
                return
                
            with self.app.app_context():
                with self.lock:
                    job = ScanJob.query.get(self.job_id)
                    if job:
                        job.progress = min(progress, 100)
                        job.machines_found = self.machines_found
                        db.session.commit()
                        logger.info(f"Job {self.job_id}: Updated progress to {progress}%")
                    else:
                        logger.error(f"Job {self.job_id}: Job not found in database")
        except Exception as e:
            logger.error(f"Job {self.job_id}: Error updating progress: {str(e)}")
            
    def scan_network(self):
        try:
            self.scanning = True
            self.current_phase = "discovery"
            self.scanned_hosts = 0
            logger.info(f"Job {self.job_id}: Starting host discovery on subnet {self.subnet}")
            
            monitor_thread = threading.Thread(target=self.monitor_progress)
            monitor_thread.start()
            
            # 主机发现
            discovery_results = self.nm.scan(
                hosts=self.subnet,
                arguments='-sn -T4 --stats-every 1s'
            )

            active_hosts = [
                host for host in discovery_results['scan']
                if discovery_results['scan'][host].get('status', {}).get('state') == 'up'
            ]

            self._save_discovery_result(active_hosts)
            
            self.total_hosts = len(active_hosts)
            logger.info(f"Job {self.job_id}: Found {self.total_hosts} active hosts")
            self.current_phase = "port_scan"
            
            # 端口扫描
            for i, host in enumerate(active_hosts, 1):
                logger.info(f"Job {self.job_id}: Scanning ports for host {i}/{self.total_hosts}: {host}")
                port_results = self.nm.scan(
                    hosts=host,
                    arguments='-sS -p- -T4 --stats-every 1s'
                )
                
                if host in port_results['scan']:
                    open_ports = []
                    for port in port_results['scan'][host].get('tcp', {}):
                        if port_results['scan'][host]['tcp'][port]['state'] == 'open':
                            open_ports.append(port)
                    
                    if open_ports:
                        with self.lock:
                            self.machines_found += 1
                            self._save_result(host, open_ports)
                            logger.info(f"Job {self.job_id}: Found {len(open_ports)} open ports on {host}")
            
            self.scanned_hosts += 1  # 更新已扫描主机数
            
            self.scanning = False
            monitor_thread.join()
            self._update_progress(100)
            logger.info(f"Job {self.job_id}: Scan completed successfully")
            return True
            
        except Exception as e:
            self.scanning = False
            logger.error(f"Job {self.job_id}: Scan execution error: {str(e)}")
            return False
                
    def _save_result(self, ip: str, open_ports: list):
        try:
            result = ScanResult(
                job_id=self.job_id,
                ip_address=ip,
                open_ports=','.join(map(str, open_ports))
            )
            db.session.add(result)
            db.session.commit()
        except Exception as e:
            print(f"Error saving result: {str(e)}")
    
    def _save_discovery_result(self, active_hosts):
        # 处理扫描结果
        scanned_ips = set()
        for host in active_hosts:
            ip_address = host
            scanned_ips.add(ip_address)
                
            # 更新或创建 IP 记录
            ip = IP.query.filter_by(ip_address=ip_address).first()
            if ip:
                ip.last_scanned = datetime.utcnow()
                if ip.status == 'inactive':
                    ip.status = 'unclaimed'
            else:
                ip = IP(
                    ip_address=ip_address,
                    status='unclaimed',
                    last_scanned=datetime.utcnow()
                )
                db.session.add(ip)
        
        # 标记未响应的 IP 为 inactive
        IP.query.filter(
            IP.ip_address.notin_(scanned_ips),
            IP.status != 'inactive'
        ).update({
            'status': 'inactive',
            'last_scanned': datetime.utcnow()
        }, synchronize_session=False)
        
        db.session.commit()
    
    def execute(self):
        return self.scan_network() 