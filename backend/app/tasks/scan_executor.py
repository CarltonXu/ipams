import nmap
import threading
import time
from datetime import datetime
from flask import current_app
from app.models.models import db, ScanJob, ScanResult, IP
from app.tasks.task_state import task_state
import os
import psutil

class ScanExecutor:
    def __init__(self, job_id: str, subnet: str, threads: int = 10):
        self.job_id = job_id
        self.subnet = subnet
        self.threads = threads
        self.lock = threading.Lock()
        self.machines_found = 0
        self.nm = nmap.PortScanner()
        self.scanning = False
        self.current_phase = "discovery"
        self.app = current_app._get_current_object()
        self.cancelled = False
        self.current_scan_process = None
        self.monitor_thread = None
        self.app.logger.info(f"Initializing scan executor for job {job_id} on subnet {subnet}")
        
    def monitor_progress(self):
        """监控扫描进度"""
        last_progress = -1
        start_time = time.time()
        
        with self.app.app_context():
            while self.scanning:
                try:
                    if self.current_phase == "discovery":
                        # 主机发现阶段，使用时间估算进度
                        elapsed = time.time() - start_time
                        # 假设主机发现需要5秒
                        current_progress = min(int((elapsed / 5) * 30), 30)
                    else:
                        # 端口扫描阶段，根据已扫描主机数计算进度
                        if not hasattr(self, 'total_hosts') or self.total_hosts == 0:
                            current_progress = 30
                        else:
                            host_percentage = (self.scanned_hosts / self.total_hosts) * 70
                            current_progress = 30 + int(host_percentage)
                    
                    if current_progress != last_progress:
                        self.app.logger.info(f"Job {self.job_id}: {self.current_phase} progress: {current_progress}%")
                        self._update_progress(current_progress)
                        last_progress = current_progress
                        
                    time.sleep(0.5)  # 更频繁地更新进度
                    
                except Exception as e:
                    self.app.logger.error(f"Progress monitoring error: {str(e)}")
        
    def _update_progress(self, progress: int):
        """更新扫描进度"""
        try:
            with self.lock:
                try:
                    job = ScanJob.query.get(self.job_id)
                    if job:
                        job.progress = min(progress, 100)
                        job.machines_found = self.machines_found
                        db.session.commit()
                        self.app.logger.info(f"Job {self.job_id}: Updated progress to {progress}%")
                    else:
                        self.app.logger.error(f"Job {self.job_id}: Job not found in database")
                except Exception as e:
                    db.session.rollback()
                    self.app.logger.error(f"Job {self.job_id}: Database error updating progress: {str(e)}")
        except Exception as e:
            self.app.logger.error(f"Job {self.job_id}: Error updating progress: {str(e)}")
            
    def cancel(self):
        """取消扫描任务"""
        self.cancelled = True
        self.scanning = False
        
        # 停止当前的 nmap 进程
        if self.current_scan_process:
            try:
                self.app.logger.info(f"Job {self.job_id}: Stopping current nmap process")
                # 获取 nmap 进程的 PID
                if hasattr(self.nm, 'get_nmap_pid'):
                    pid = self.nm.get_nmap_pid()
                    if pid:
                        import signal
                        try:
                            os.kill(pid, signal.SIGTERM)
                            self.app.logger.info(f"Job {self.job_id}: Sent SIGTERM to nmap process {pid}")
                        except ProcessLookupError:
                            self.app.logger.warning(f"Job {self.job_id}: Nmap process {pid} not found")
                        except Exception as e:
                            self.app.logger.error(f"Job {self.job_id}: Error killing nmap process: {str(e)}")
                
                # 尝试终止所有相关的 nmap 进程
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if 'nmap' in proc.info['name'].lower():
                                cmdline = ' '.join(proc.info['cmdline'] or [])
                                if self.subnet in cmdline:
                                    proc.terminate()
                                    self.app.logger.info(f"Job {self.job_id}: Terminated nmap process {proc.info['pid']}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                except Exception as e:
                    self.app.logger.error(f"Job {self.job_id}: Error terminating nmap processes: {str(e)}")
                
                self.current_scan_process = None
            except Exception as e:
                self.app.logger.error(f"Job {self.job_id}: Error stopping nmap process: {str(e)}")
        
        self.app.logger.info(f"Job {self.job_id}: Scan cancelled")
        
        # 更新任务状态为已取消
        try:
            with self.lock:
                job = ScanJob.query.get(self.job_id)
                if job:
                    job.status = 'cancelled'
                    job.end_time = datetime.utcnow()
                    db.session.commit()
                    self.app.logger.info(f"Job {self.job_id}: Status updated to cancelled")
        except Exception as e:
            self.app.logger.error(f"Job {self.job_id}: Error updating status to cancelled: {str(e)}")
            db.session.rollback()

    def cleanup(self):
        """清理资源"""
        try:
            self.scanning = False
            self.cancelled = True
            
            # 停止当前的 nmap 进程
            if self.current_scan_process:
                try:
                    self.app.logger.info(f"Job {self.job_id}: Stopping current nmap process")
                    # 获取 nmap 进程的 PID
                    if hasattr(self.nm, 'get_nmap_pid'):
                        pid = self.nm.get_nmap_pid()
                        if pid:
                            import signal
                            try:
                                os.kill(pid, signal.SIGTERM)
                                self.app.logger.info(f"Job {self.job_id}: Sent SIGTERM to nmap process {pid}")
                            except ProcessLookupError:
                                self.app.logger.warning(f"Job {self.job_id}: Nmap process {pid} not found")
                            except Exception as e:
                                self.app.logger.error(f"Job {self.job_id}: Error killing nmap process: {str(e)}")
                    
                    # 尝试终止所有相关的 nmap 进程
                    try:
                        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                            try:
                                if 'nmap' in proc.info['name'].lower():
                                    cmdline = ' '.join(proc.info['cmdline'] or [])
                                    if self.subnet in cmdline:
                                        proc.terminate()
                                        self.app.logger.info(f"Job {self.job_id}: Terminated nmap process {proc.info['pid']}")
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass
                    except Exception as e:
                        self.app.logger.error(f"Job {self.job_id}: Error terminating nmap processes: {str(e)}")
                    
                    self.current_scan_process = None
                except Exception as e:
                    self.app.logger.error(f"Job {self.job_id}: Error stopping nmap process: {str(e)}")
            
            # 等待监控线程结束
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.app.logger.info(f"Job {self.job_id}: Waiting for monitor thread to finish")
                self.monitor_thread.join(timeout=5)
                if self.monitor_thread.is_alive():
                    self.app.logger.warning(f"Job {self.job_id}: Monitor thread did not terminate within timeout")
            
            self.app.logger.info(f"Job {self.job_id}: Cleanup completed")
        except Exception as e:
            self.app.logger.error(f"Job {self.job_id}: Error during cleanup: {str(e)}")

    def scan_network(self):
        try:
            self.scanning = True
            self.current_phase = "discovery"
            self.scanned_hosts = 0
            self.app.logger.info(f"Job {self.job_id}: Starting host discovery on subnet {self.subnet}")
            
            # 更新任务状态为运行中
            try:
                job = ScanJob.query.get(self.job_id)
                if job:
                    job.status = 'running'
                    db.session.commit()
                    self.app.logger.info(f"Job {self.job_id}: Status updated to running")
            except Exception as e:
                self.app.logger.error(f"Job {self.job_id}: Error updating initial status: {str(e)}")
                db.session.rollback()
            
            # 启动监控线程
            self.monitor_thread = threading.Thread(target=self.monitor_progress)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            # 主机发现
            try:
                self.current_scan_process = self.nm.scan(
                    hosts=self.subnet,
                    arguments='-sn -T5 --stats-every 1s'
                )
            except Exception as e:
                self.app.logger.error(f"Job {self.job_id}: Error during host discovery: {str(e)}")
                return False

            # 检查是否被取消
            if self.cancelled:
                self.app.logger.info(f"Job {self.job_id}: Scan cancelled during discovery phase")
                return False

            active_hosts = [
                host for host in self.current_scan_process['scan']
                if self.current_scan_process['scan'][host].get('status', {}).get('state') == 'up'
            ]

            self._save_discovery_result(active_hosts)
            
            self.total_hosts = len(active_hosts)
            self.app.logger.info(f"Job {self.job_id}: Found {self.total_hosts} active hosts")
            
            if self.total_hosts == 0:
                self.scanning = False
                self.monitor_thread.join(timeout=5)
                self._update_progress(100)
                return True
                
            self.current_phase = "port_scan"

            # 获取扫描端口配置
            scan_ports = self.app.config.get("SCAN_PORTS", "80,443,22,21,23,25,53,110,143,3306,3389,5432,6379,8080,8443")
            self.app.logger.info(f"Job {self.job_id}: Using scan ports: {scan_ports}")

            # 端口扫描
            for i, host in enumerate(active_hosts, 1):
                # 检查是否被取消
                if self.cancelled:
                    self.app.logger.info(f"Job {self.job_id}: Scan cancelled during port scan phase")
                    return False

                self.app.logger.info(f"Job {self.job_id}: Starting port scan for host {i}/{self.total_hosts}: {host}")
                try:
                    # 使用更简单的扫描参数，添加超时控制
                    self.app.logger.info(f"Job {self.job_id}: Executing nmap scan for {host}")
                    self.current_scan_process = self.nm.scan(
                        hosts=host,
                        arguments=f'-sT -p {scan_ports} -T4 --host-timeout 10s --max-rtt-timeout 500ms --max-retries 1'
                    )
                    
                    # 检查是否被取消
                    if self.cancelled:
                        self.app.logger.info(f"Job {self.job_id}: Scan cancelled during port scan phase")
                        return False
                    
                    self.app.logger.info(f"Job {self.job_id}: Port scan results for {host}: {self.current_scan_process}")
                    
                    if host in self.current_scan_process['scan']:
                        open_ports = []
                        try:
                            for port in self.current_scan_process['scan'][host].get('tcp', {}):
                                if self.current_scan_process['scan'][host]['tcp'][port]['state'] == 'open':
                                    open_ports.append(port)
                            
                            if open_ports:
                                self.machines_found += 1
                                self._save_result(host, open_ports)
                                self.app.logger.info(f"Job {self.job_id}: Found {len(open_ports)} open ports on {host}")
                            else:
                                self.app.logger.info(f"Job {self.job_id}: No open ports found on {host}")
                        except Exception as e:
                            self.app.logger.error(f"Job {self.job_id}: Error processing scan results for {host}: {str(e)}")
                    else:
                        self.app.logger.warning(f"Job {self.job_id}: No scan results for host {host}")
                        
                except Exception as e:
                    self.app.logger.error(f"Job {self.job_id}: Port scan failed for host {host}: {str(e)}")
                    continue
                finally:
                    try:
                        # 更新已扫描主机数
                        self.scanned_hosts += 1
                        self.app.logger.info(f"Job {self.job_id}: Completed scanning host {i}/{self.total_hosts}: {host}")
                    except Exception as e:
                        self.app.logger.error(f"Job {self.job_id}: Error updating scan progress: {str(e)}")
                
                # 添加短暂延迟，让进度更新更平滑
                time.sleep(0.5)
            
            # 扫描完成
            self.app.logger.info(f"Job {self.job_id}: All hosts scanned, updating final status")
            self.scanning = False
            
            # 清理资源
            self.cleanup()
            
            # 更新最终进度
            try:
                self._update_progress(100)
            except Exception as e:
                self.app.logger.error(f"Job {self.job_id}: Error updating final progress: {str(e)}")
            
            # 更新任务状态为完成
            try:
                job = ScanJob.query.get(self.job_id)
                if job:
                    job.status = 'completed'
                    job.end_time = datetime.utcnow()
                    db.session.commit()
                    self.app.logger.info(f"Job {self.job_id}: Status updated to completed")
                else:
                    self.app.logger.error(f"Job {self.job_id}: Failed to update status - job not found")
            except Exception as e:
                self.app.logger.error(f"Job {self.job_id}: Error updating final status: {str(e)}")
                db.session.rollback()
            
            self.app.logger.info(f"Job {self.job_id}: Scan completed successfully")
            return True
            
        except Exception as e:
            self.scanning = False
            self.app.logger.error(f"Job {self.job_id}: Scan execution error: {str(e)}")
            
            # 清理资源
            self.cleanup()
            
            # 更新任务状态为失败
            with self.lock:
                job = ScanJob.query.get(self.job_id)
                if job:
                    job.status = 'failed'
                    job.error_message = str(e)
                    job.end_time = datetime.utcnow()
                    db.session.commit()
            
            return False
                
    def _save_result(self, ip: str, open_ports: list):
        try:
            try:
                job = ScanJob.query.get(self.job_id)
                if not job:
                    self.app.logger.error(f"Job {self.job_id} not found when saving result")
                    return
                    
                result = ScanResult(
                    job_id=self.job_id,
                    ip_address=ip,
                    open_ports=','.join(map(str, open_ports))
                )
                db.session.add(result)
                db.session.commit()
                self.app.logger.info(f"Saved scan result for job {self.job_id}, IP {ip}")
            except Exception as e:
                db.session.rollback()
                self.app.logger.error(f"Database error saving result for job {self.job_id}: {str(e)}")
        except Exception as e:
            self.app.logger.error(f"Error saving result for job {self.job_id}: {str(e)}")
    
    def _save_discovery_result(self, active_hosts):
        try:
            try:
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
                self.app.logger.info(f"Saved discovery results for job {self.job_id}")
            except Exception as e:
                db.session.rollback()
                self.app.logger.error(f"Database error saving discovery results for job {self.job_id}: {str(e)}")
        except Exception as e:
            self.app.logger.error(f"Error saving discovery results for job {self.job_id}: {str(e)}")
    
    def execute(self):
        """执行扫描任务"""
        try:
            with self.app.app_context():
                self.app.logger.info(f"Starting scan execution for job {self.job_id}")
                result = self.scan_network()
                self.app.logger.info(f"Scan execution completed for job {self.job_id} with result: {result}")
                return result
        except Exception as e:
            self.app.logger.error(f"Error executing scan for job {self.job_id}: {str(e)}")
            return False 