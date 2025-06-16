import logging
import nmap
import os
import psutil
import time
import threading
import xml.etree.ElementTree as ET

from typing import Optional, Dict
from datetime import datetime

from flask import current_app
from app.models.models import db, ScanJob, ScanResult, IP
from app.core.utils.logger import app_logger as logger
from app.services.notification.events import NotificationEvent, send_notification

class ScanExecutor:
    def __init__(self, job_id: str, subnet: str, threads: int = 5, scan_params: Optional[Dict] = None):
        self.job_id = job_id
        self.subnet = subnet
        self.threads = threads
        self.scan_params = scan_params or {}
        self.lock = threading.Lock()
        self.machines_found = 0
        self.nm = nmap.PortScanner()
        self.scanning = False
        self.current_phase = "discovery"
        self.app = current_app._get_current_object()
        self.notification_manager = current_app.notification_manager
        self.cancelled = False
        self.current_scan_process = None
        self.monitor_thread = None
        self.job_user_id = None
        logger.info(f"Initializing scan executor for job {job_id} on subnet {subnet}")
        
    def _load_job_user_id(self):
        """加载任务的user_id"""
        with self.app.app_context():
            job = ScanJob.query.get(self.job_id)
            if job:
                self.job_user_id = job.user_id

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
                        logger.info(f"Job {self.job_id}: {self.current_phase} progress: {current_progress}%")
                        self._update_progress(current_progress)
                        last_progress = current_progress
                        
                    time.sleep(0.5)  # 更频繁地更新进度
                    
                except Exception as e:
                    logger.error(f"Progress monitoring error: {str(e)}")
        
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
                        logger.info(f"Job {self.job_id}: Updated progress to {progress}%")
                    else:
                        logger.error(f"Job {self.job_id}: Job not found in database")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Job {self.job_id}: Database error updating progress: {str(e)}")
        except Exception as e:
            logger.error(f"Job {self.job_id}: Error updating progress: {str(e)}")
            
    def cancel(self):
        """取消扫描任务"""
        self.cancelled = True
        self.scanning = False
        
        logger.info(f"Job {self.job_id}: Starting cancellation process")
        logger.info(f"Job {self.job_id}: current_scan_process status: {self.current_scan_process is not None}")
        
        # 停止当前的 nmap 进程
        if self.current_scan_process:
            try:
                logger.info(f"Job {self.job_id}: Stopping current nmap process")
                # 获取 nmap 进程的 PID
                if hasattr(self.nm, 'get_nmap_pid'):
                    pid = self.nm.get_nmap_pid()
                    if pid:
                        import signal
                        try:
                            os.kill(pid, signal.SIGTERM)
                            logger.info(f"Job {self.job_id}: Sent SIGTERM to nmap process {pid}")
                        except ProcessLookupError:
                            logger.warning(f"Job {self.job_id}: Nmap process {pid} not found")
                        except Exception as e:
                            logger.error(f"Job {self.job_id}: Error killing nmap process: {str(e)}")
                
                # 尝试终止所有相关的 nmap 进程
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if 'nmap' in proc.info['name'].lower():
                                cmdline = ' '.join(proc.info['cmdline'] or [])
                                if self.subnet in cmdline:
                                    proc.terminate()
                                    logger.info(f"Job {self.job_id}: Terminated nmap process {proc.info['pid']}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                except Exception as e:
                    logger.error(f"Job {self.job_id}: Error terminating nmap processes: {str(e)}")
                
                self.current_scan_process = None
            except Exception as e:
                logger.error(f"Job {self.job_id}: Error stopping nmap process: {str(e)}")
        else:
            logger.info(f"Job {self.job_id}: No active nmap process to stop")
        
        logger.info(f"Job {self.job_id}: Scan cancelled")
        
        # 更新任务状态为已取消
        try:
            with self.lock:
                job = ScanJob.query.get(self.job_id)
                if job:
                    job.status = 'cancelled'
                    job.end_time = datetime.utcnow()
                    db.session.commit()
                    logger.info(f"Job {self.job_id}: Status updated to cancelled")
        except Exception as e:
            logger.error(f"Job {self.job_id}: Error updating status to cancelled: {str(e)}")
            db.session.rollback()

    def cleanup(self):
        """清理资源"""
        try:
            self.scanning = False
            self.cancelled = True
            
            # 停止当前的 nmap 进程
            if self.current_scan_process:
                try:
                    logger.info(f"Job {self.job_id}: Stopping current nmap process")
                    # 获取 nmap 进程的 PID
                    if hasattr(self.nm, 'get_nmap_pid'):
                        pid = self.nm.get_nmap_pid()
                        if pid:
                            import signal
                            try:
                                os.kill(pid, signal.SIGTERM)
                                logger.info(f"Job {self.job_id}: Sent SIGTERM to nmap process {pid}")
                            except ProcessLookupError:
                                logger.warning(f"Job {self.job_id}: Nmap process {pid} not found")
                            except Exception as e:
                                logger.error(f"Job {self.job_id}: Error killing nmap process: {str(e)}")
                    
                    # 尝试终止所有相关的 nmap 进程
                    try:
                        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                            try:
                                if 'nmap' in proc.info['name'].lower():
                                    cmdline = ' '.join(proc.info['cmdline'] or [])
                                    if self.subnet in cmdline:
                                        proc.terminate()
                                        logger.info(f"Job {self.job_id}: Terminated nmap process {proc.info['pid']}")
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass
                    except Exception as e:
                        logger.error(f"Job {self.job_id}: Error terminating nmap processes: {str(e)}")
                    
                    self.current_scan_process = None
                except Exception as e:
                    logger.error(f"Job {self.job_id}: Error stopping nmap process: {str(e)}")
            
            # 等待监控线程结束
            if self.monitor_thread and self.monitor_thread.is_alive():
                logger.info(f"Job {self.job_id}: Waiting for monitor thread to finish")
                self.monitor_thread.join(timeout=5)
                if self.monitor_thread.is_alive():
                    logger.warning(f"Job {self.job_id}: Monitor thread did not terminate within timeout")
            
            logger.info(f"Job {self.job_id}: Cleanup completed")
        except Exception as e:
            logger.error(f"Job {self.job_id}: Error during cleanup: {str(e)}")

    def scan_network(self):
        try:
            with self.app.app_context():
                self.scanning = True
                self.current_phase = "discovery"
                self.scanned_hosts = 0
                logger.info(f"Job {self.job_id}: Starting host discovery on subnet {self.subnet}")
                logger.info(f"Job {self.job_id}: Initial current_scan_process status: {self.current_scan_process is not None}")

                # 检查是否已取消
                if self.cancelled:
                    logger.info(f"Job {self.job_id}: Scan cancelled before starting")
                    return False

                self._load_job_user_id()
                
                # 更新任务状态为运行中
                try:
                    job = ScanJob.query.get(self.job_id)
                    if job:
                        job.status = 'running'
                        db.session.commit()
                        logger.info(f"Job {self.job_id}: Status updated to running")
                except Exception as e:
                    logger.error(f"Job {self.job_id}: Error updating initial status: {str(e)}")
                    db.session.rollback()
                
                # 启动监控线程
                self.monitor_thread = threading.Thread(target=self.monitor_progress)
                self.monitor_thread.daemon = True
                self.monitor_thread.start()
                
                # 主机发现
                try:
                    # 检查是否已取消
                    if self.cancelled:
                        logger.info(f"Job {self.job_id}: Scan cancelled before host discovery")
                        return False

                    logger.info(f"Job {self.job_id}: Starting nmap scan for host discovery")
                    self.current_scan_process = self.nm.scan(
                        hosts=self.subnet,
                        arguments='-sn -T5 --stats-every 1s'
                    )
                    logger.info(f"Job {self.job_id}: Host discovery scan completed, current_scan_process status: {self.current_scan_process is not None}")
                except Exception as e:
                    logger.error(f"Job {self.job_id}: Error during host discovery: {str(e)}")
                    return False

                # 检查是否被取消
                if self.cancelled:
                    logger.info(f"Job {self.job_id}: Scan cancelled during discovery phase")
                    return False

                active_hosts = [
                    host for host in self.current_scan_process['scan']
                    if self.current_scan_process['scan'][host].get('status', {}).get('state') == 'up'
                ]

                self._save_discovery_result(active_hosts)
                
                self.total_hosts = len(active_hosts)
                logger.info(f"Job {self.job_id}: Found {self.total_hosts} active hosts")
                
                if self.total_hosts == 0:
                    self.scanning = False
                    self.monitor_thread.join(timeout=5)
                    self._update_progress(100)
                    return True
                    
                self.current_phase = "port_scan"

                # 获取扫描端口配置
                scan_ports = self.app.config.get("SCAN_PORTS", "80,443,22,21,23,25,53,110,143,3306,3389,5432,6379,8080,8443")
                
                # 构建扫描参数
                scan_args = '-sT -T4 --host-timeout 10s --max-rtt-timeout 500ms --max-retries 1'
                
                # 如果启用了自定义扫描类型，添加相应的参数
                if self.scan_params.get('enable_custom_scan_type'):
                    scan_type = self.scan_params.get('scan_type', 'default')
                    if scan_type == 'quick':
                        scan_args = '-sT -T4 -F --host-timeout 10s --max-rtt-timeout 500ms --max-retries 1'
                        scan_ports = None
                        logger.info(f"Job {self.job_id}: Using quick scan mode (top 100 ports)")
                    elif scan_type == 'intense':
                        scan_args = '-sT -T4 -A -v --host-timeout 10s --max-rtt-timeout 500ms --max-retries 1'
                        if self.scan_params.get('enable_custom_ports') and self.scan_params.get('ports'):
                            scan_ports = self.scan_params['ports']
                            logger.info(f"Job {self.job_id}: Using intense scan mode with custom ports: {scan_ports}")
                        else:
                            scan_ports = None
                            logger.info(f"Job {self.job_id}: Using intense scan mode (all ports)")
                    elif scan_type == 'vulnerability':
                        scan_args = '-sT -T4 -A -v --script vuln --host-timeout 10s --max-rtt-timeout 500ms --max-retries 1'
                        if self.scan_params.get('enable_custom_ports') and self.scan_params.get('ports'):
                            scan_ports = self.scan_params['ports']
                            logger.info(f"Job {self.job_id}: Using vulnerability scan mode with custom ports: {scan_ports}")
                        else:
                            scan_ports = None
                            logger.info(f"Job {self.job_id}: Using vulnerability scan mode (all ports)")
                else:
                    if self.scan_params.get('enable_custom_ports') and self.scan_params.get('ports'):
                        scan_ports = self.scan_params['ports']
                        logger.info(f"Job {self.job_id}: Using default scan mode with custom ports: {scan_ports}")
                    else:
                        logger.info(f"Job {self.job_id}: Using default scan mode with default ports: {scan_ports}")

                # 端口扫描
                for i, host in enumerate(active_hosts, 1):
                    # 检查是否被取消
                    if self.cancelled:
                        logger.info(f"Job {self.job_id}: Scan cancelled during port scan phase")
                        return False

                    logger.info(f"Job {self.job_id}: Starting port scan for host {i}/{self.total_hosts}: {host}")
                    try:
                        # 使用配置的扫描参数
                        logger.info(f"Job {self.job_id}: Executing nmap scan for {host}")
                        scan_arguments = scan_args
                        if scan_ports:
                            scan_arguments += f' -p {scan_ports}'
                        
                        # 检查是否被取消
                        if self.cancelled:
                            logger.info(f"Job {self.job_id}: Scan cancelled before starting port scan for {host}")
                            return False
                        
                        logger.info(f"Job {self.job_id}: Starting port scan for {host}, current_scan_process status before scan: {self.current_scan_process is not None}")
                        self.current_scan_process = self.nm.scan(
                            hosts=host,
                            arguments=scan_arguments
                        )
                        logger.info(f"Job {self.job_id}: Port scan completed for {host}, current_scan_process status after scan: {self.current_scan_process is not None}")
                        
                        # 检查是否被取消
                        if self.cancelled:
                            logger.info(f"Job {self.job_id}: Scan cancelled during port scan for {host}")
                            return False
                        
                        logger.info(f"Job {self.job_id}: Port scan results for {host}: {self.current_scan_process}")
                        
                        if host in self.current_scan_process['scan']:
                            open_ports = []
                            try:
                                for port in self.current_scan_process['scan'][host].get('tcp', {}):
                                    if self.current_scan_process['scan'][host]['tcp'][port]['state'] == 'open':
                                        open_ports.append(port)
                                
                                if open_ports:
                                    self.machines_found += 1
                                    self._save_result(host, open_ports)
                                    logger.info(f"Job {self.job_id}: Found {len(open_ports)} open ports on {host}")
                                else:
                                    logger.info(f"Job {self.job_id}: No open ports found on {host}")
                            except Exception as e:
                                logger.error(f"Job {self.job_id}: Error processing scan results for {host}: {str(e)}")
                        else:
                            logger.warning(f"Job {self.job_id}: No scan results for host {host}")
                            
                    except Exception as e:
                        logger.error(f"Job {self.job_id}: Port scan failed for host {host}: {str(e)}")
                        continue
                    finally:
                        try:
                            # 更新已扫描主机数
                            self.scanned_hosts += 1
                            logger.info(f"Job {self.job_id}: Completed scanning host {i}/{self.total_hosts}: {host}")
                        except Exception as e:
                            logger.error(f"Job {self.job_id}: Error updating scan progress: {str(e)}")
                    
                    # 检查是否被取消
                    if self.cancelled:
                        logger.info(f"Job {self.job_id}: Scan cancelled after scanning host {host}")
                        return False
                    
                    # 添加短暂延迟，让进度更新更平滑
                    time.sleep(0.5)
                
                # 扫描完成
                logger.info(f"Job {self.job_id}: All hosts scanned, updating final status")
                self.scanning = False
                
                # 清理资源
                self.cleanup()
                
                # 更新最终进度
                try:
                    self._update_progress(100)
                except Exception as e:
                    logger.error(f"Job {self.job_id}: Error updating final progress: {str(e)}")
                
                # 更新任务状态为完成
                try:
                    job = ScanJob.query.get(self.job_id)
                    if job:
                        job.status = 'completed'
                        job.end_time = datetime.utcnow()
                        db.session.commit()
                        logger.info(f"Job {self.job_id}: Status updated to completed")
                    else:
                        logger.error(f"Job {self.job_id}: Failed to update status - job not found")
                except Exception as e:
                    logger.error(f"Job {self.job_id}: Error updating final status: {str(e)}")
                    db.session.rollback()
                
                logger.info(f"Job {self.job_id}: Scan completed successfully")
                return True
                
        except Exception as e:
            self.scanning = False
            logger.error(f"Job {self.job_id}: Scan execution error: {str(e)}")
            
            # 清理资源
            self.cleanup()
            
            # 更新任务状态为失败
            with self.app.app_context():
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
                    logger.error(f"Job {self.job_id} not found when saving result")
                    return
                
                # 构建端口信息字典
                ports_info = {}
                for port in open_ports:
                    port_info = self.current_scan_process['scan'][ip]['tcp'][port]
                    ports_info[str(port)] = {
                        'protocol': 'tcp',
                        'service': port_info.get('name', ''),
                        'version': port_info.get('version', ''),
                        'banner': port_info.get('banner', ''),
                        'state': port_info.get('state', '')
                    }
                
                result = ScanResult(
                    job_id=self.job_id,
                    ip_address=ip,
                    open_ports=ports_info,
                    status='up',
                    raw_data=self.current_scan_process['scan'][ip]
                )
                db.session.add(result)
                db.session.commit()
                logger.info(f"Saved scan result for job {self.job_id}, IP {ip}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error saving result for job {self.job_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error saving result for job {self.job_id}: {str(e)}")
    
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
                            # 发送IP地址状态变更通知
                            if self.job_user_id:
                                self.notification_manager.create_notification(
                                    user_id=self.job_user_id,
                                    title="IP地址状态变更",
                                    content=f"IP地址 {ip_address} 的状态已从 'inactive' 变为 'unclaimed'。",
                                    type="ip",
                                    commit=True
                                )
                                logger.info(f"Sent notification for IP status change {ip_address} to user {self.job_user_id}")
                    else:
                        ip = IP(
                            ip_address=ip_address,
                            status='unclaimed',
                            last_scanned=datetime.utcnow()
                        )
                        db.session.add(ip)
                        # 发送新IP地址发现通知
                        if self.job_user_id:
                            self.notification_manager.create_notification(
                                user_id=self.job_user_id,
                                title="新IP地址发现",
                                content=f"在扫描 {self.subnet} 时发现了新的IP地址: {ip_address}",
                                type="ip",
                                commit=True
                            )
                            logger.info(f"Sent notification for new IP {ip_address} to user {self.job_user_id}")
                
                # 标记未响应的 IP 为 inactive
                IP.query.filter(
                    IP.ip_address.notin_(scanned_ips),
                    IP.status != 'inactive'
                ).update({
                    'status': 'inactive',
                    'last_scanned': datetime.utcnow()
                }, synchronize_session=False)
                
                db.session.commit()
                logger.info(f"Saved discovery results for job {self.job_id}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error saving discovery results for job {self.job_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error saving discovery results for job {self.job_id}: {str(e)}")
    
    def execute(self):
        """执行扫描任务"""
        try:
            with self.app.app_context():
                logger.info(f"Starting scan execution for job {self.job_id}")
                result = self.scan_network()
                logger.info(f"Scan execution completed for job {self.job_id} with result: {result}")

                # 扫描完成后发送通知
                job = ScanJob.query.get(self.job_id)
                if job:
                    if result:
                        send_notification(
                            event=NotificationEvent.SCAN_COMPLETED,
                            user=job.user,
                            template_data={
                                'job_name': job.policy.name,
                                'subnet': self.subnet,
                                'machines_found': self.machines_found
                            }
                        )
                    else:
                        send_notification(
                            event=NotificationEvent.SCAN_FAILED,
                            user=job.user,
                            template_data={
                                'job_name': job.policy.name,
                                'subnet': self.subnet,
                                'error': job.error_message
                            }
                        )
                else:
                    logger.error(f"Job {self.job_id}: Failed to update status - job not found")

                return result
        except Exception as e:
            logger.error(f"Error executing scan for job {self.job_id}: {str(e)}")
            return False 