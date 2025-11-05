"""
采集管理器
统一管理采集任务，支持批量采集和单个主机采集
实现采集任务队列和并发控制
"""
import threading
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from flask import current_app
from app.models.models import db, HostInfo, CollectionTask, Credential, CollectionProgress
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
            
            # 执行采集（collect_single_host不支持progress_callback）
            result = self._execute_collection(host_info, credential, custom_port=custom_credential.get('port') if custom_credential else None, progress_callback=None)
            
            # 更新结果
            host_ip = host_info.ip.ip_address if host_info.ip else 'Unknown'
            if result['success']:
                host_info.collection_status = 'success'
                host_info.last_collected_at = datetime.utcnow()
                host_info.collection_error = None
                
                # 更新主机信息
                collection_data = result.get('data', {})
                self._update_host_info(host_info, collection_data)
                
                # 如果是VMware批量采集，需要创建子主机记录
                vm_count = 0
                if isinstance(collection_data, dict) and 'vms' in collection_data:
                    vm_count = len(collection_data['vms'])
                    self._create_vm_child_records(host_info, collection_data['vms'])
                
                if vm_count > 0:
                    logger.info(
                        f"主机信息采集成功: {host_ip} (类型: {host_info.host_type or 'Unknown'}, 发现 {vm_count} 个VM)",
                        extra={
                            'host_id': host_info.id,
                            'host_ip': host_ip,
                            'host_type': host_info.host_type,
                            'vm_count': vm_count,
                            'operation': 'host_collect_success'
                        }
                    )
                else:
                    logger.info(
                        f"主机信息采集成功: {host_ip} (类型: {host_info.host_type or 'Unknown'})",
                        extra={
                            'host_id': host_info.id,
                            'host_ip': host_ip,
                            'host_type': host_info.host_type,
                            'operation': 'host_collect_success'
                        }
                    )
            else:
                host_info.collection_status = 'failed'
                error_msg = result.get('error', 'Unknown error')
                host_info.collection_error = error_msg
                logger.warning(
                    f"主机信息采集失败: {host_ip} - {error_msg}",
                    extra={
                        'host_id': host_info.id,
                        'host_ip': host_ip,
                        'error': error_msg,
                        'operation': 'host_collect_failed'
                    }
                )
            
            db.session.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error collecting single host: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _collect_single_host_with_progress(self, host_info_id: str, progress_callback: Optional[Callable] = None,
                                           credential_id: Optional[str] = None, 
                                           custom_credential: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        采集单个主机信息（支持进度回调，主要用于VMware批量采集）
        
        Args:
            host_info_id: 主机信息ID
            credential_id: 凭证ID（可选）
            custom_credential: 自定义凭证（可选）
            progress_callback: 进度回调函数
            
        Returns:
            采集结果字典
        """
        try:
            host_info = HostInfo.query.get(host_info_id)
            if not host_info:
                return {'success': False, 'error': 'Host not found'}
            
            # 获取凭证
            credential_obj = None
            use_custom = False
            
            if custom_credential:
                use_custom = True
            elif credential_id:
                credential_obj = Credential.query.filter_by(
                    id=credential_id,
                    user_id=host_info.ip.assigned_user_id if host_info.ip else None,
                    deleted=False
                ).first()
            
            if not credential_obj and not use_custom:
                # 尝试获取绑定的凭证
                from app.models.models import HostCredentialBinding
                binding = HostCredentialBinding.query.filter_by(
                    host_id=host_info_id
                ).first()
                if binding:
                    credential_obj = Credential.query.filter_by(
                        id=binding.credential_id,
                        deleted=False
                    ).first()
                else:
                    return {'success': False, 'error': 'No credential available'}
            
            # 检查凭证类型，判断是否为VMware
            credential_type = None
            if custom_credential:
                credential_type = custom_credential.get('credential_type')
            elif credential_obj:
                credential_type = credential_obj.credential_type
            
            is_vmware = host_info.host_type == 'vmware' or credential_type == 'vmware'
            
            if is_vmware and progress_callback:
                # 对于VMware，使用带进度回调的采集
                result = self._execute_vmware_collection_with_progress(
                    host_info, credential_obj, custom_credential, progress_callback
                )
            else:
                # 其他情况使用普通采集（但如果是VMware，也传递progress_callback）
                result = self._execute_collection(
                    host_info, credential_obj, 
                    custom_port=custom_credential.get('port') if custom_credential else None,
                    progress_callback=progress_callback if is_vmware else None
                )
            
            # 更新结果
            host_ip = host_info.ip.ip_address if host_info.ip else 'Unknown'
            if result['success']:
                host_info.collection_status = 'success'
                host_info.last_collected_at = datetime.utcnow()
                host_info.collection_error = None
                
                # 更新主机信息
                collection_data = result.get('data', {})
                self._update_host_info(host_info, collection_data)
                
                # 如果是VMware批量采集，需要创建子主机记录
                vm_count = 0
                if isinstance(collection_data, dict) and 'vms' in collection_data:
                    vm_count = len(collection_data['vms'])
                    self._create_vm_child_records(host_info, collection_data['vms'])
                
                if vm_count > 0:
                    logger.info(
                        f"主机信息采集成功: {host_ip} (类型: {host_info.host_type or 'Unknown'}, 发现 {vm_count} 个VM)",
                        extra={
                            'host_id': host_info.id,
                            'host_ip': host_ip,
                            'host_type': host_info.host_type,
                            'vm_count': vm_count,
                            'operation': 'host_collect_success'
                        }
                    )
                else:
                    logger.info(
                        f"主机信息采集成功: {host_ip} (类型: {host_info.host_type or 'Unknown'})",
                        extra={
                            'host_id': host_info.id,
                            'host_ip': host_ip,
                            'host_type': host_info.host_type,
                            'operation': 'host_collect_success'
                        }
                    )
            else:
                host_info.collection_status = 'failed'
                error_msg = result.get('error', 'Unknown error')
                host_info.collection_error = error_msg
                logger.warning(
                    f"主机信息采集失败: {host_ip} - {error_msg}",
                    extra={
                        'host_id': host_info.id,
                        'host_ip': host_ip,
                        'error': error_msg,
                        'operation': 'host_collect_failed'
                    }
                )
            
            db.session.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error collecting single host with progress: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _execute_vmware_collection_with_progress(self, host_info: HostInfo, credential: Optional[Credential],
                                                custom_credential: Optional[Dict[str, Any]],
                                                progress_callback: Callable) -> Dict[str, Any]:
        """
        执行VMware采集（带进度回调）
        """
        try:
            ip_address = host_info.ip.ip_address if host_info.ip else None
            if not ip_address:
                return {'success': False, 'error': 'Host IP not found'}
            
            # 获取凭证信息
            if custom_credential:
                username = custom_credential.get('username')
                password = custom_credential.get('password')
            elif credential:
                username = decrypt_credential(credential.username) if credential.username else None
                password = decrypt_credential(credential.password) if credential.password else None
            else:
                return {'success': False, 'error': 'No credential available'}
            
            if progress_callback is None:
                logger.error("progress_callback is None in _execute_vmware_collection_with_progress!")
                return {'success': False, 'error': 'Progress callback is None'}
            
            # 调用VMware采集器（传递进度回调）
            from flask import current_app
            max_workers = current_app.config.get('VMWARE_COLLECTION_MAX_WORKERS', 10) if current_app else 10
            
            vm_data = self.vmware_collector.collect_vm_info(
                vcenter_host=ip_address,
                username=username,
                password=password,
                collect_all_vms=True,
                progress_callback=progress_callback,
                max_workers=max_workers
            )
            
            if isinstance(vm_data, list):
                return {
                    'success': True,
                    'data': {
                        'host_type': 'vmware',
                        'vms': vm_data
                    }
                }
            else:
                return {
                    'success': True,
                    'data': vm_data
                }
                
        except Exception as e:
            logger.error(f"Error executing VMware collection with progress: {str(e)}")
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
        from flask import current_app
        
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
            
            # 在主线程中获取task_id（字符串），避免跨线程访问对象
            task_id = task.id
            
            # 刷新会话，确保对象完全持久化
            db.session.refresh(task)
            
            # 获取当前应用实例，用于在线程中使用
            app = current_app._get_current_object() if current_app else None
            if not app:
                raise RuntimeError("Cannot get Flask application instance")
            
            # 包装执行函数，确保应用上下文正确传递，并传递app实例
            def execute_with_context():
                with app.app_context():
                    self._execute_batch_collection(task_id, host_ids, app)
            
            # 在后台线程中执行采集
            threading.Thread(
                target=execute_with_context,
                daemon=True
            ).start()
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating batch collection task: {str(e)}")
            raise
    
    def _execute_batch_collection(self, task_id: str, host_ids: List[str], app=None):
        """
        执行批量采集
        
        Args:
            task_id: 任务ID
            host_ids: 主机ID列表
            app: Flask应用实例（用于传递到子线程）
        """
        # 注意：此方法应该在应用上下文中调用
        try:
            # 更新任务状态
            task = CollectionTask.query.get(task_id)
            if not task:
                logger.error(f"CollectionTask {task_id} not found")
                return
            
            task.status = 'running'
            db.session.commit()
            
            # 创建或获取进度记录
            progress = CollectionProgress.query.filter_by(task_id=task_id).first()
            if not progress:
                progress = CollectionProgress(
                    task_id=task_id,
                    total_count=len(host_ids),
                    completed_count=0,
                    failed_count=0,
                    status='running',
                    current_step=f'开始采集 {len(host_ids)} 台主机'
                )
                db.session.add(progress)
                db.session.commit()
            else:
                progress.status = 'running'
                progress.total_count = len(host_ids)
                progress.completed_count = 0
                progress.failed_count = 0
                progress.current_step = f'开始采集 {len(host_ids)} 台主机'
                db.session.commit()
            
            logger.info(
                f"批量采集任务已启动: 任务ID={task_id}, 主机数量={len(host_ids)}",
                extra={
                    'task_id': task_id,
                    'host_count': len(host_ids),
                    'operation': 'batch_collect_start'
                }
            )
            
            success_count = 0
            failed_count = 0
            
            # 获取应用实例用于子线程（如果没有传递，则从current_app获取）
            if app is None:
                from flask import current_app
                app = current_app._get_current_object()
            
            # 限制并发数
            for i in range(0, len(host_ids), self.max_concurrent):
                batch = host_ids[i:i + self.max_concurrent]
                
                threads = []
                for host_id in batch:
                    def collect_with_context(host_id, task_id, app_instance):
                        with app_instance.app_context():
                            self._collect_in_batch(host_id, task_id, app_instance)
                    
                    thread = threading.Thread(
                        target=collect_with_context,
                        args=(host_id, task_id, app),
                        daemon=True
                    )
                    
                    thread.start()
                    threads.append(thread)
                
                # 等待批次完成
                for thread in threads:
                    thread.join()
            
            # 最终统计结果
            progress = CollectionProgress.query.filter_by(task_id=task_id).first()
            if progress:
                progress.status = 'completed'
                progress.current_step = '采集完成'
                progress.updated_at = datetime.utcnow()
            
            task.status = 'completed'
            task.end_time = datetime.utcnow()
            db.session.commit()
            
            logger.info(
                f"批量采集任务已完成: 任务ID={task_id}, 成功={task.success_count}, 失败={task.failed_count}, 总计={task.total_hosts}",
                extra={
                    'task_id': task_id,
                    'success_count': task.success_count,
                    'failed_count': task.failed_count,
                    'total_hosts': task.total_hosts,
                    'operation': 'batch_collect_completed'
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing batch collection: {str(e)}", extra={'task_id': task_id})
            from flask import current_app
            app = current_app._get_current_object()
            with app.app_context():
                task = CollectionTask.query.get(task_id)
                progress = CollectionProgress.query.filter_by(task_id=task_id).first()
                if task:
                    task.status = 'failed'
                if progress:
                    progress.status = 'failed'
                    progress.error_message = str(e)
                db.session.commit()
    
    def _collect_in_batch(self, host_id: str, task_id: str, app=None):
        """
        在批次中采集单个主机
        
        Args:
            host_id: 主机ID
            task_id: 任务ID
            app: Flask应用实例（用于传递到回调函数）
        
        注意：此方法应该在应用上下文中调用
        """
        try:
            host_info = HostInfo.query.get(host_id)
            if not host_info:
                logger.error(f"HostInfo {host_id} not found")
                return
            
            host_ip = host_info.ip.ip_address if host_info.ip else host_id
            host_type = host_info.host_type or 'Unknown'
            
            logger.info(
                f"开始采集主机信息: {host_ip} (类型: {host_type})",
                extra={
                    'host_id': host_id,
                    'host_ip': host_ip,
                    'host_type': host_type,
                    'task_id': task_id,
                    'operation': 'host_collect_start'
                }
            )
            
            # 获取进度记录并更新当前步骤
            progress = CollectionProgress.query.filter_by(task_id=task_id).first()
            if progress:
                progress.current_step = f'正在采集主机: {host_ip}'
                db.session.commit()
            
            # 如果是VMware主机，需要设置进度回调来更新进度
            # 获取应用实例，用于在回调中使用（优先使用传递的app，否则从current_app获取）
            if app is None:
                from flask import current_app
                callback_app = current_app._get_current_object() if current_app else None
            else:
                callback_app = app
            
            if callback_app is None:
                logger.error(f"Cannot get Flask application instance for callback, task_id: {task_id}")
                return
            
            # 定义进度回调函数
            def progress_callback(completed: int, total: int, vm_info: Dict[str, Any] = None):
                """VMware采集进度回调"""
                # 确保在应用上下文中执行数据库操作
                if callback_app is None:
                    logger.error(f"callback_app is None, cannot update progress, task_id: {task_id}")
                    return
                
                with callback_app.app_context():
                    try:
                        progress = CollectionProgress.query.filter_by(task_id=task_id).first()
                        if not progress:
                            logger.warning(f"CollectionProgress not found for task_id: {task_id}")
                            return
                        
                        # 如果这是第一次回调，更新total_count
                        if progress.total_count == 1 and total > 1:
                            # 原来只有1个（父主机），现在需要加上VM数量
                            progress.total_count = 1 + total  # 1个父主机 + N个VM
                        
                        # 更新已完成数量（父主机 + 已完成的VM）
                        # completed是已完成的VM数量
                        progress.completed_count = 1 + completed  # 1个父主机 + 已完成的VM数量
                        
                        # 更新当前步骤
                        vm_name = None
                        if vm_info:
                            # 尝试从不同路径获取VM名称
                            if isinstance(vm_info, dict):
                                vm_name = vm_info.get('vm_name') or vm_info.get('hostname') or vm_info.get('vmware_info', {}).get('vm_name')
                        
                        if vm_name:
                            progress.current_step = f'正在采集VM: {vm_name} ({completed}/{total})'
                        else:
                            progress.current_step = f'正在采集VM ({completed}/{total})'
                        
                        progress.updated_at = datetime.utcnow()
                        db.session.commit()
                        
                        # 每采集5个VM或最后一个VM时输出日志
                        if completed % 5 == 0 or completed == total:
                            logger.info(
                                f"VMware采集进度: {completed}/{total} VM已完成",
                                extra={
                                    'task_id': task_id,
                                    'host_id': host_id,
                                    'completed': completed,
                                    'total': total,
                                    'progress_percent': round(completed / total * 100, 1) if total > 0 else 0,
                                    'operation': 'vmware_collect_progress'
                                }
                            )
                    except Exception as e:
                        logger.error(
                            f"Error updating progress in callback: {str(e)}",
                            extra={'task_id': task_id, 'completed': completed, 'total': total},
                            exc_info=True
                        )
            
            # 执行采集（如果是VMware，传递进度回调）
            # 检查凭证类型，判断是否为VMware（因为host_type可能为None）
            credential_type = None
            from app.models.models import HostCredentialBinding, Credential
            binding = HostCredentialBinding.query.filter_by(host_id=host_id).first()
            if binding:
                cred = Credential.query.get(binding.credential_id)
                if cred and not cred.deleted:
                    credential_type = cred.credential_type
            
            is_vmware = host_info.host_type == 'vmware' or credential_type == 'vmware'
            
            if is_vmware:
                # 对于VMware，需要传递进度回调
                if progress_callback is None:
                    logger.error(f"progress_callback is None for VMware host! host_id={host_id}, task_id={task_id}")
                result = self._collect_single_host_with_progress(host_id, progress_callback)
            else:
                result = self.collect_single_host(host_id)
            
            # 更新任务计数和进度
            task = CollectionTask.query.get(task_id)
            progress = CollectionProgress.query.filter_by(task_id=task_id).first()
            
            if result['success']:
                task.success_count += 1
                if progress:
                    # 对于VMware，completed_count已经在回调中更新了
                    # 这里确保至少是1（父主机采集完成）
                    if host_info.host_type != 'vmware' or progress.completed_count == 0:
                        progress.completed_count += 1
                    
                    # 如果VMware采集完成，total_count应该包含所有VM
                    if host_info.host_type == 'vmware' and 'vms' in result.get('data', {}):
                        vm_count = len(result['data'].get('vms', []))
                        if progress.total_count == 1:
                            progress.total_count = 1 + vm_count
            else:
                task.failed_count += 1
                error_msg = result.get('error', 'Collection returned no data')
                host_info.collection_error = error_msg
                
                if progress:
                    progress.failed_count += 1
                    # 将错误信息追加到进度记录中
                    host_ip = host_info.ip.ip_address if host_info.ip else host_id
                    error_entry = f"[{host_ip}] {error_msg}"
                    
                    # 如果已有错误信息，追加新的；否则创建新的
                    if progress.error_message:
                        # 检查是否已有该主机的错误信息，避免重复
                        if f"[{host_ip}]" not in progress.error_message:
                            progress.error_message = progress.error_message + "\n" + error_entry
                    else:
                        progress.error_message = error_entry
                    
                    # 限制错误信息长度，避免过长
                    if progress.error_message and len(progress.error_message) > 2000:
                        # 只保留最新的错误信息
                        lines = progress.error_message.split('\n')
                        progress.error_message = '\n'.join(lines[-10:])  # 保留最后10条错误
            
            if progress:
                progress.updated_at = datetime.utcnow()
                # 计算进度百分比
                if progress.total_count > 0:
                    progress_percent = (progress.completed_count + progress.failed_count) / progress.total_count * 100
                    progress.current_step = f'已完成 {progress.completed_count + progress.failed_count}/{progress.total_count} ({progress_percent:.1f}%)'
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error collecting host {host_id} in batch: {str(e)}", extra={'host_id': host_id, 'task_id': task_id})
            from flask import current_app
            app = current_app._get_current_object()
            with app.app_context():
                task = CollectionTask.query.get(task_id)
                progress = CollectionProgress.query.filter_by(task_id=task_id).first()
                host_info = HostInfo.query.get(host_id)
                
                error_msg = str(e)
                if host_info:
                    host_info.collection_error = error_msg
                    host_ip = host_info.ip.ip_address if host_info.ip else host_id
                else:
                    host_ip = host_id
                
                if task:
                    task.failed_count += 1
                if progress:
                    progress.failed_count += 1
                    progress.updated_at = datetime.utcnow()
                    
                    # 将异常错误信息追加到进度记录中
                    error_entry = f"[{host_ip}] 采集异常: {error_msg}"
                    if progress.error_message:
                        if f"[{host_ip}]" not in progress.error_message:
                            progress.error_message = progress.error_message + "\n" + error_entry
                    else:
                        progress.error_message = error_entry
                    
                    # 限制错误信息长度
                    if progress.error_message and len(progress.error_message) > 2000:
                        lines = progress.error_message.split('\n')
                        progress.error_message = '\n'.join(lines[-10:])
                
                db.session.commit()
    
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
        from app.models.models import HostCredentialBinding
        binding = HostCredentialBinding.query.filter_by(host_id=host_info.id).first()
        if binding:
            credential = Credential.query.get(binding.credential_id)
            if credential and not credential.deleted:
                return credential
        
        # 尝试获取默认凭证
        default_credential = Credential.query.filter_by(
            user_id=host_info.ip.assigned_user_id,
            is_default=True,
            deleted=False
        ).first()
        
        return default_credential
    
    def _execute_collection(self, host_info: HostInfo, credential: Any, custom_port: Optional[int] = None, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        执行采集
        
        Args:
            host_info: 主机信息
            credential: 凭证对象或字典
            custom_port: 自定义端口号
            progress_callback: 进度回调函数（用于VMware采集）
            
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
                from flask import current_app
                max_workers = current_app.config.get('VMWARE_COLLECTION_MAX_WORKERS', 10) if current_app else 10
                
                logger.info(
                    f"Using _execute_collection for VMware with progress_callback={progress_callback is not None}",
                    extra={
                        'host_id': host_info.id,
                        'host_ip': host_info.ip.ip_address if host_info.ip else None,
                        'has_progress_callback': progress_callback is not None,
                        'operation': 'execute_collection_vmware'
                    }
                )
                
                result = self.vmware_collector.collect_vm_info(
                    vcenter_host=host_info.ip.ip_address,
                    username=username,
                    password=password,
                    collect_all_vms=True,
                    progress_callback=progress_callback,
                    max_workers=max_workers
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
            
            # 检查返回结果格式
            if isinstance(result, dict):
                # 如果结果已经是标准格式（包含 success 字段），直接返回
                if 'success' in result:
                    if result.get('success'):
                        return {'success': True, 'data': result.get('data', result)}
                    else:
                        # 失败情况，返回错误信息
                        return {'success': False, 'error': result.get('error', 'Collection failed')}
                # 如果结果是非空字典但没有 success 字段，认为是成功的数据
                elif result:
                    return {'success': True, 'data': result}
            
            # 空结果或非字典类型
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
            # 对于VMware主机，优先使用vm_name作为hostname
            if 'vmware_info' in data and isinstance(data['vmware_info'], dict):
                vm_name = data['vmware_info'].get('vm_name')
                if vm_name:
                    host_info.hostname = vm_name
                else:
                    host_info.hostname = data.get('hostname') or host_info.hostname
            else:
                host_info.hostname = data.get('hostname') or host_info.hostname
            
            host_info.os_name = data.get('os_name') or host_info.os_name
            host_info.os_version = data.get('os_version') or host_info.os_version
            host_info.kernel_version = data.get('kernel_version') or host_info.kernel_version
            host_info.cpu_model = data.get('cpu_model') or host_info.cpu_model
            host_info.cpu_cores = data.get('cpu_cores') or host_info.cpu_cores
            host_info.memory_total = data.get('memory_total') or host_info.memory_total
            host_info.memory_free_mb = data.get('memory_free_mb') or host_info.memory_free_mb
            host_info.os_bit = data.get('os_bit') or host_info.os_bit
            host_info.boot_method = data.get('boot_method') or host_info.boot_method
            host_info.disk_info = data.get('disk_info') or host_info.disk_info
            host_info.network_interfaces = data.get('network_interfaces') or host_info.network_interfaces
            
            # 计算聚合字段：磁盘数量
            if data.get('disk_info'):
                disk_info_list = data['disk_info']
                if isinstance(disk_info_list, list):
                    host_info.disk_count = len(disk_info_list)
                else:
                    host_info.disk_count = 0
            elif host_info.disk_info:
                if isinstance(host_info.disk_info, list):
                    host_info.disk_count = len(host_info.disk_info)
                else:
                    host_info.disk_count = 0
            else:
                host_info.disk_count = None
            
            # 计算聚合字段：总磁盘容量（GB）
            if data.get('disk_info'):
                host_info.disk_total_gb = self._calculate_total_disk_size(data['disk_info'])
            elif host_info.disk_info:
                host_info.disk_total_gb = self._calculate_total_disk_size(host_info.disk_info)
            else:
                host_info.disk_total_gb = None
            
            # 计算聚合字段：网卡数量
            if data.get('network_interfaces'):
                network_list = data['network_interfaces']
                if isinstance(network_list, list):
                    host_info.network_count = len(network_list)
                else:
                    host_info.network_count = 0
            elif host_info.network_interfaces:
                if isinstance(host_info.network_interfaces, list):
                    host_info.network_count = len(host_info.network_interfaces)
                else:
                    host_info.network_count = 0
            else:
                host_info.network_count = None
            
            # VMware信息单独处理
            if 'vmware_info' in data:
                host_info.vmware_info = data['vmware_info']
            
            # 保存原始数据
            host_info.raw_data = data
            
        except Exception as e:
            logger.error(f"Error updating host info: {str(e)}")
    
    def _calculate_total_disk_size(self, disk_info: Any) -> Optional[float]:
        """
        计算总磁盘容量（GB）
        
        Args:
            disk_info: 磁盘信息列表（可能是列表或JSON）
            
        Returns:
            总容量（GB），如果无法计算则返回None
        """
        try:
            if not disk_info:
                return None
            
            if not isinstance(disk_info, list):
                # 如果是JSON字符串，尝试解析
                import json
                if isinstance(disk_info, str):
                    disk_info = json.loads(disk_info)
                else:
                    return None
            
            total_gb = 0.0
            
            for disk in disk_info:
                if not isinstance(disk, dict):
                    continue
                
                # 尝试多种字段名和格式
                size_value = None
                
                # VMware格式：capacity_kb
                if 'capacity_kb' in disk and disk['capacity_kb']:
                    size_value = float(disk['capacity_kb']) / 1024.0 / 1024.0  # KB to GB
                # VMware格式：capacity_bytes
                elif 'capacity_bytes' in disk and disk['capacity_bytes']:
                    size_value = float(disk['capacity_bytes']) / 1024.0 / 1024.0 / 1024.0  # Bytes to GB
                # Linux/Windows格式：size（可能是字符串如"100G"或数字）
                elif 'size' in disk:
                    size_str = str(disk['size']).strip()
                    # 尝试解析字符串格式（如"100G", "50GB", "1000M"）
                    if size_str:
                        # 转换为小写并提取数字和单位
                        size_str_lower = size_str.lower()
                        if 'g' in size_str_lower or 'gb' in size_str_lower:
                            # 提取数字部分
                            import re
                            match = re.search(r'[\d.]+', size_str)
                            if match:
                                size_value = float(match.group())
                        elif 'm' in size_str_lower or 'mb' in size_str_lower:
                            import re
                            match = re.search(r'[\d.]+', size_str)
                            if match:
                                size_value = float(match.group()) / 1024.0  # MB to GB
                        elif 't' in size_str_lower or 'tb' in size_str_lower:
                            import re
                            match = re.search(r'[\d.]+', size_str)
                            if match:
                                size_value = float(match.group()) * 1024.0  # TB to GB
                        else:
                            # 尝试直接转换为数字（假设是GB）
                            try:
                                size_value = float(size_str)
                            except ValueError:
                                pass
                # Windows格式：Size（已经是GB）
                elif 'Size' in disk and disk['Size']:
                    try:
                        size_value = float(disk['Size'])
                    except (ValueError, TypeError):
                        pass
                
                if size_value is not None:
                    total_gb += size_value
            
            return round(total_gb, 2) if total_gb > 0 else None
            
        except Exception as e:
            logger.warning(f"Error calculating total disk size: {str(e)}")
            return None
    
    def _create_vm_child_records(self, parent_host: HostInfo, vm_list: List[Dict[str, Any]]):
        """
        为VMware采集结果创建子主机记录（批量优化版本）
        
        Args:
            parent_host: 父主机（vCenter）
            vm_list: 虚拟机列表
        """
        try:
            if not vm_list:
                logger.warning(f"No VM list provided for parent host {parent_host.id}")
                return
            
            # 一次性查询所有现有子记录，避免N+1查询问题
            existing_children = HostInfo.query.filter_by(
                parent_host_id=parent_host.id,
                deleted=False
            ).all()
            
            # 构建UUID到子主机的映射，提高查找效率
            uuid_to_child_map = {}
            for child in existing_children:
                if child.vmware_info and isinstance(child.vmware_info, dict):
                    vm_uuid = child.vmware_info.get('vm_uuid')
                    if vm_uuid:
                        uuid_to_child_map[vm_uuid] = child
            
            # 分离需要创建和更新的记录
            new_children = []
            update_children = []
            skipped_count = 0
            
            for vm_info in vm_list:
                vmware_info = vm_info.get('vmware_info', {})
                vm_uuid = vmware_info.get('vm_uuid')
                vm_name = vmware_info.get('vm_name') or vm_info.get('hostname') or 'Unknown'
                if not vm_uuid:
                    skipped_count += 1
                    logger.warning(
                        f"VM信息缺少vm_uuid，已跳过: VM名称={vm_name}",
                        extra={
                            'parent_host_id': parent_host.id,
                            'vm_name': vm_name,
                            'vm_info_keys': list(vm_info.keys()),
                            'operation': 'vm_uuid_missing'
                        }
                    )
                    continue
                
                if vm_uuid in uuid_to_child_map:
                    # 已存在，准备更新
                    existing_child = uuid_to_child_map[vm_uuid]
                    update_children.append((existing_child, vm_info))
                else:
                    # 新记录，准备创建
                    child_host = HostInfo(
                        ip_id=parent_host.ip_id,  # 子主机共享父主机的IP
                        parent_host_id=parent_host.id,
                        host_type='vmware',  # 子主机也是VMware类型
                        collection_status='success',
                        last_collected_at=datetime.utcnow()
                    )
                    # 先更新基本信息，使计算字段能正确计算
                    self._update_host_info(child_host, vm_info)
                    new_children.append(child_host)
            
            # 批量插入新记录
            if new_children:
                try:
                    db.session.bulk_save_objects(new_children, return_defaults=True)
                    db.session.flush()  # 刷新以获取ID
                    logger.info(
                        f"Bulk created {len(new_children)} VM child records",
                        extra={
                            'parent_host_id': parent_host.id,
                            'new_count': len(new_children),
                            'operation': 'bulk_create_vm_children'
                        }
                    )
                except Exception as e:
                    logger.error(f"Error bulk inserting VM child records: {str(e)}")
                    db.session.rollback()
                    raise
            
            # 批量更新已有记录
            for existing_child, vm_info in update_children:
                try:
                    self._update_host_info(existing_child, vm_info)
                except Exception as e:
                    logger.error(
                        f"Error updating VM child record {existing_child.id}: {str(e)}",
                        extra={
                            'child_host_id': existing_child.id,
                            'vm_uuid': vm_info.get('vmware_info', {}).get('vm_uuid'),
                            'operation': 'update_vm_child'
                        }
                    )
            
                        # 提交所有更改
            db.session.commit()
            
            logger.info(
                f"VM child records processed: {len(new_children)} created, {len(update_children)} updated, {skipped_count} skipped",
                extra={
                    'parent_host_id': parent_host.id,
                    'created_count': len(new_children),
                    'updated_count': len(update_children),
                    'skipped_count': skipped_count,
                    'total_vms': len(vm_list),
                    'operation': 'create_vm_child_records'
                }
            )
                
        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Error creating VM child records: {str(e)}",
                extra={
                    'parent_host_id': parent_host.id,
                    'vm_count': len(vm_list) if vm_list else 0,
                    'error': str(e),
                    'operation': 'create_vm_child_records'
                }
            )
            raise


# 创建全局实例
collector_manager = CollectorManager()

