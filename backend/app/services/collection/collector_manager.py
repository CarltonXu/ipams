"""
采集管理器
统一管理采集任务，支持批量采集和单个主机采集
实现采集任务队列和并发控制
"""
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
from flask import current_app
from app.models.models import db, HostInfo, CollectionTask, Credential
from app.core.utils.logger import app_logger as logger
from app.core.security.encryption import decrypt_credential
from .ansible_collector import AnsibleCollector
from .vmware_collector import VMwareCollector


class CollectorManager:
    """采集管理器单例"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CollectorManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.ansible_collector = AnsibleCollector()
        self.vmware_collector = VMwareCollector()
        self.max_concurrent = 5
        self.timeout = 300
        self._active_tasks = {}
        self._task_lock = threading.Lock()
    
    def init_app(self, app):
        """初始化应用配置"""
        with app.app_context():
            self.max_concurrent = app.config.get('COLLECTION_MAX_CONCURRENT', 5)
            self.timeout = app.config.get('COLLECTION_TIMEOUT', 300)
    
    def collect_single_host(self, host_info_id: str, credential_id: Optional[str] = None, 
                           custom_credential: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        采集单个主机信息
        
        Args:
            host_info_id: 主机信息ID
            credential_id: 凭证ID（可选，如果不提供则使用绑定默认凭证）
            custom_credential: 自定义凭证字典，包含username, password, private_key, port等
            
        Returns:
            采集结果
        """
        try:
            host_info = HostInfo.query.get(host_info_id)
            if not host_info:
                return {'success': False, 'error': 'Host info not found'}
            
            # 更新采集状态
            host_info.collection_status = 'collecting'
            host_info.collection_error = None
            db.session.commit()
            
            # 确定使用哪个凭证
            if custom_credential:
                # 使用自定义凭证
                credential_type = custom_credential.get('credential_type') or 'linux'
                credential = {
                    'username': custom_credential.get('username'),
                    'password': custom_credential.get('password'),
                    'private_key': custom_credential.get('private_key'),
                    'credential_type': credential_type
                }
                use_custom = True
            else:
                # 获取绑定或默认凭证
                credential_obj = self._get_credential(host_info, credential_id)
                if not credential_obj:
                    host_info.collection_status = 'failed'
                    host_info.collection_error = 'No credential available'
                    db.session.commit()
                    return {'success': False, 'error': 'No credential available'}
                credential = credential_obj
                use_custom = False
            
            # 执行采集
            result = self._execute_collection(host_info, credential, custom_port=custom_credential.get('port') if custom_credential else None)
            
            # 更新结果
            if result['success']:
                host_info.collection_status = 'success'
                host_info.last_collected_at = datetime.utcnow()
                host_info.collection_error = None
                
                # 更新主机信息
                collection_data = result.get('data', {})
                self._update_host_info(host_info, collection_data)
                
                # 如果是VMware批量采集，需要创建子主机记录
                if isinstance(collection_data, dict) and 'vms' in collection_data:
                    self._create_vm_child_records(host_info, collection_data['vms'])
            else:
                host_info.collection_status = 'failed'
                host_info.collection_error = result.get('error', 'Unknown error')
            
            db.session.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error collecting single host: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def collect_batch_hosts(self, host_ids: List[str], user_id: str) -> str:
        """
        批量采集主机信息
        
        Args:
            host_ids: 主机信息ID列表
            user_id: 用户ID
            
        Returns:
            采集任务ID
        """
        try:
            # 创建采集任务
            task = CollectionTask(
                user_id=user_id,
                trigger_type='manual',
                status='pending',
                total_hosts=len(host_ids)
            )
            db.session.add(task)
            db.session.commit()
            
            # 在后台线程中执行采集
            threading.Thread(
                target=self._execute_batch_collection,
                args=(task.id, host_ids),
                daemon=True
            ).start()
            
            return task.id
            
        except Exception as e:
            logger.error(f"Error creating batch collection task: {str(e)}")
            raise
    
    def _execute_batch_collection(self, task_id: str, host_ids: List[str]):
        """
        执行批量采集
        
        Args:
            task_id: 任务ID
            host_ids: 主机ID列表
        """
        try:
            # 更新任务状态
            task = CollectionTask.query.get(task_id)
            task.status = 'running'
            db.session.commit()
            
            success_count = 0
            failed_count = 0
            
            # 限制并发数
            for i in range(0, len(host_ids), self.max_concurrent):
                batch = host_ids[i:i + self.max_concurrent]
                
                threads = []
                for host_id in batch:
                    thread = threading.Thread(
                        target=self._collect_in_batch,
                        args=(host_id, task_id),
                        daemon=True
                    )
                    thread.start()
                    threads.append(thread)
                
                # 等待批次完成
                for thread in threads:
                    thread.join()
            
            # 统计结果
            task.status = 'completed'
            task.end_time = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Batch collection task {task_id} completed. Success: {success_count}, Failed: {failed_count}")
            
        except Exception as e:
            logger.error(f"Error executing batch collection: {str(e)}")
            task = CollectionTask.query.get(task_id)
            if task:
                task.status = 'failed'
                db.session.commit()
    
    def _collect_in_batch(self, host_id: str, task_id: str):
        """
        在批次中采集单个主机
        
        Args:
            host_id: 主机ID
            task_id: 任务ID
        """
        try:
            result = self.collect_single_host(host_id)
            
            # 更新任务计数
            task = CollectionTask.query.get(task_id)
            if result['success']:
                task.success_count += 1
            else:
                task.failed_count += 1
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error collecting host {host_id} in batch: {str(e)}")
    
    def _get_credential(self, host_info: HostInfo, credential_id: Optional[str] = None) -> Optional[Credential]:
        """
        获取用于采集的凭证
        
        Args:
            host_info: 主机信息
            credential_id: 凭证ID
            
        Returns:
            凭证对象
        """
        if credential_id:
            credential = Credential.query.get(credential_id)
            if credential and not credential.deleted:
                return credential
        
        # 如果没有指定凭证，使用绑定的凭证
        bindings = host_info.credential_bindings
        if bindings:
            binding = bindings[0]
            credential = binding.credential
            if credential and not credential.deleted:
                return credential
        
        # 尝试获取默认凭证
        default_credential = Credential.query.filter_by(
            user_id=host_info.ip.assigned_user_id,
            is_default=True,
            deleted=False
        ).first()
        
        return default_credential
    
    def _execute_collection(self, host_info: HostInfo, credential: Any, custom_port: Optional[int] = None) -> Dict[str, Any]:
        """
        执行采集
        
        Args:
            host_info: 主机信息
            credential: 凭证对象或字典
            custom_port: 自定义端口号
            
        Returns:
            采集结果
        """
        try:
            # 判断是对象还是字典
            if isinstance(credential, dict):
                username = credential.get('username')
                password = credential.get('password')
                private_key = credential.get('private_key')
                credential_type = credential.get('credential_type')
            else:
                # 解密凭证
                username = decrypt_credential(credential.username) if credential.username else None
                password = decrypt_credential(credential.password) if credential.password else None
                private_key = decrypt_credential(credential.private_key) if credential.private_key else None
                credential_type = credential.credential_type
            
            # 根据主机类型选择采集器
            if credential_type == 'vmware':
                # VMware采集
                vmware_info = host_info.vmware_info or {}
                result = self.vmware_collector.collect_vm_info(
                    vcenter_host=host_info.ip.ip_address,
                    username=username,
                    password=password,
                    collect_all_vms=True
                )
            elif credential_type == 'linux':
                # Linux采集
                result = self.ansible_collector.collect_linux_info(
                    host_ip=host_info.ip.ip_address,
                    username=username,
                    password=password,
                    private_key=private_key,
                    port=custom_port or 22
                )
            elif credential_type == 'windows':
                # Windows采集
                result = self.ansible_collector.collect_windows_info(
                    host_ip=host_info.ip.ip_address,
                    username=username,
                    password=password,
                    port=custom_port or 5985
                )
            else:
                return {'success': False, 'error': 'Unsupported credential type'}
            
            if result:
                return {'success': True, 'data': result}
            else:
                return {'success': False, 'error': 'Collection returned no data'}
                
        except Exception as e:
            logger.error(f"Error executing collection: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _update_host_info(self, host_info: HostInfo, data: Dict[str, Any]):
        """
        更新主机信息
        
        Args:
            host_info: 主机信息对象
            data: 采集到的数据
        """
        try:
            host_info.hostname = data.get('hostname') or host_info.hostname
            host_info.os_name = data.get('os_name') or host_info.os_name
            host_info.os_version = data.get('os_version') or host_info.os_version
            host_info.kernel_version = data.get('kernel_version') or host_info.kernel_version
            host_info.cpu_model = data.get('cpu_model') or host_info.cpu_model
            host_info.cpu_cores = data.get('cpu_cores') or host_info.cpu_cores
            host_info.memory_total = data.get('memory_total') or host_info.memory_total
            host_info.disk_info = data.get('disk_info') or host_info.disk_info
            host_info.network_interfaces = data.get('network_interfaces') or host_info.network_interfaces
            
            # VMware信息单独处理
            if 'vmware_info' in data:
                host_info.vmware_info = data['vmware_info']
            
            # 保存原始数据
            host_info.raw_data = data
            
        except Exception as e:
            logger.error(f"Error updating host info: {str(e)}")
    
    def _create_vm_child_records(self, parent_host: HostInfo, vm_list: List[Dict[str, Any]]):
        """
        为VMware采集结果创建子主机记录
        
        Args:
            parent_host: 父主机（vCenter）
            vm_list: 虚拟机列表
        """
        try:
            for vm_info in vm_list:
                # 检查是否已存在（根据VM UUID）
                vm_uuid = vm_info.get('vmware_info', {}).get('vm_uuid')
                if not vm_uuid:
                    continue
                
                # 查找是否已有子主机记录（需要匹配vm_uuid）
                existing_child = None
                children = HostInfo.query.filter_by(
                    parent_host_id=parent_host.id,
                    deleted=False
                ).all()
                
                for child in children:
                    if child.vmware_info and child.vmware_info.get('vm_uuid') == vm_uuid:
                        existing_child = child
                        break
                
                if existing_child:
                    # 更新已有记录
                    self._update_host_info(existing_child, vm_info)
                else:
                    # 创建新的子主机记录
                    child_host = HostInfo(
                        ip_id=parent_host.ip_id,  # 子主机共享父主机的IP
                        parent_host_id=parent_host.id,
                        host_type='vmware',  # 子主机也是VMware类型
                        collection_status='success',
                        last_collected_at=datetime.utcnow()
                    )
                    db.session.add(child_host)
                    db.session.flush()  # 获取ID后更新信息
                    
                    # 更新子主机信息
                    self._update_host_info(child_host, vm_info)
                    
                logger.info(f"Created/updated VM child record for {vm_info.get('hostname', 'unknown')}")
                
        except Exception as e:
            logger.error(f"Error creating VM child records: {str(e)}")


# 创建全局实例
collector_manager = CollectorManager()

