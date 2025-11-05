"""
Ansible 主机信息采集器
使用 ansible-runner 或 subprocess 调用 ansible 命令采集主机信息
"""
import os
import json
import tempfile
from typing import Dict, Any, Optional
from flask import current_app
from app.core.utils.logger import app_logger as logger
from app.core.security.encryption import decrypt_credential


class AnsibleCollector:
    """Ansible 主机信息采集器"""
    
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), 'playbooks')
        self.ansible_timeout = current_app.config.get('ANSIBLE_TIMEOUT', 30) if current_app else 30
    
    def collect_linux_info(self, host_ip: str, username: str, password: Optional[str] = None, 
                          private_key: Optional[str] = None, port: int = 22) -> Dict[str, Any]:
        """
        采集Linux主机信息
        
        Args:
            host_ip: 主机IP地址
            username: 用户名
            password: 密码（可选）
            private_key: SSH私钥（可选）
            port: SSH端口号
            
        Returns:
            采集的主机信息字典
        """
        try:
            logger.info(
                "Linux collection started",
                extra={
                    'host_ip': host_ip,
                    'username': username,
                    'port': port,
                    'operation': 'linux_collect'
                }
            )
            
            playbook_path = os.path.join(self.base_dir, 'linux_info.yml')
            
            # 准备inventory文件
            inventory_content = self._prepare_inventory(host_ip, username, password, private_key, 'linux', port)
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 写入inventory文件
                inventory_file = os.path.join(tmp_dir, 'inventory.ini')
                with open(inventory_file, 'w') as f:
                    f.write(inventory_content)
                
                # 执行ansible playbook
                result = self._run_playbook(playbook_path, inventory_file, tmp_dir)
                
                if result.get('success'):
                    host_info = self._parse_linux_result(result)
                    # 检查解析结果是否为空
                    if not host_info:
                        error_msg = 'Failed to parse collection result or no data collected'
                        logger.warning(
                            f"Linux collection result is empty for {host_ip}: {error_msg}",
                            extra={
                                'host_ip': host_ip,
                                'error': error_msg,
                                'operation': 'linux_collect'
                            }
                        )
                        return {'success': False, 'error': error_msg}
                    
                    logger.info(
                        "Linux collection completed",
                        extra={
                            'host_ip': host_ip,
                            'hostname': host_info.get('hostname'),
                            'operation': 'linux_collect'
                        }
                    )
                    return host_info
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(
                        f"Failed to collect Linux info from {host_ip}: {error_msg}",
                        extra={
                            'host_ip': host_ip,
                            'error': error_msg,
                            'operation': 'linux_collect'
                        }
                    )
                    # 返回包含错误信息的字典，而不是空字典
                    return {'success': False, 'error': error_msg}
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"Error collecting Linux info from {host_ip}: {error_msg}",
                extra={
                    'host_ip': host_ip,
                    'error': error_msg,
                    'operation': 'linux_collect'
                }
            )
            # 返回包含错误信息的字典，而不是空字典
            return {'success': False, 'error': error_msg}
    
    def collect_windows_info(self, host_ip: str, username: str, password: str, port: int = 5985) -> Dict[str, Any]:
        """
        采集Windows主机信息
        
        Args:
            host_ip: 主机IP地址
            username: 用户名
            password: 密码
            port: WinRM端口号
            
        Returns:
            采集的主机信息字典
        """
        try:
            logger.info(
                "Windows collection started",
                extra={
                    'host_ip': host_ip,
                    'username': username,
                    'port': port,
                    'operation': 'windows_collect'
                }
            )
            
            playbook_path = os.path.join(self.base_dir, 'windows_info.yml')
            
            # 准备inventory文件
            inventory_content = self._prepare_inventory(host_ip, username, password, None, 'windows', port)
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 写入inventory文件
                inventory_file = os.path.join(tmp_dir, 'inventory.ini')
                with open(inventory_file, 'w') as f:
                    f.write(inventory_content)
                
                # 执行ansible playbook
                result = self._run_playbook(playbook_path, inventory_file, tmp_dir)
                
                if result.get('success'):
                    host_info = self._parse_windows_result(result)
                    # 检查解析结果是否为空
                    if not host_info:
                        error_msg = 'Failed to parse collection result or no data collected'
                        logger.warning(
                            f"Windows collection result is empty for {host_ip}: {error_msg}",
                            extra={
                                'host_ip': host_ip,
                                'error': error_msg,
                                'operation': 'windows_collect'
                            }
                        )
                        return {'success': False, 'error': error_msg}
                    
                    logger.info(
                        "Windows collection completed",
                        extra={
                            'host_ip': host_ip,
                            'hostname': host_info.get('hostname'),
                            'operation': 'windows_collect'
                        }
                    )
                    return host_info
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(
                        f"Failed to collect Windows info from {host_ip}: {error_msg}",
                        extra={
                            'host_ip': host_ip,
                            'error': error_msg,
                            'operation': 'windows_collect'
                        }
                    )
                    # 返回包含错误信息的字典，而不是空字典
                    return {'success': False, 'error': error_msg}
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"Error collecting Windows info from {host_ip}: {error_msg}",
                extra={
                    'host_ip': host_ip,
                    'error': error_msg,
                    'operation': 'windows_collect'
                }
            )
            # 返回包含错误信息的字典，而不是空字典
            return {'success': False, 'error': error_msg}
    
    def _prepare_inventory(self, host_ip: str, username: str, password: Optional[str], 
                          private_key: Optional[str], os_type: str, port: int) -> str:
        """
        准备Ansible inventory内容
        
        Args:
            host_ip: 主机IP
            username: 用户名
            password: 密码
            private_key: SSH私钥
            os_type: 操作系统类型
            port: 端口号
            
        Returns:
            inventory文件内容
        """
        if os_type == 'windows':
            # Windows主机使用winrm
            return f"""[all]
{host_ip} ansible_user={username} ansible_password={password} ansible_connection=winrm ansible_winrm_transport=basic ansible_winrm_port={port}
"""
        else:
            # Linux主机使用SSH
            auth_method = ''
            if private_key:
                # 保存私钥到临时文件
                key_file = os.path.join(tempfile.gettempdir(), f'ansible_key_{host_ip}.pem')
                with open(key_file, 'w') as f:
                    f.write(private_key)
                os.chmod(key_file, 0o600)
                auth_method = f' ansible_ssh_private_key_file={key_file}'
                if password:
                    auth_method += f' ansible_ssh_pass={password}'
            elif password:
                auth_method = f' ansible_ssh_pass={password}'
            
            return f"""[all]
{host_ip} ansible_user={username}{auth_method} ansible_connection=ssh ansible_port={port}
"""
    
    def _run_playbook(self, playbook_path: str, inventory_file: str, project_dir: str) -> Dict[str, Any]:
        """
        执行Ansible playbook
        使用ansible-runner库执行playbook
        
        Args:
            playbook_path: playbook路径
            inventory_file: inventory文件路径
            project_dir: 项目目录
            
        Returns:
            执行结果
        """
        try:
            import ansible_runner
            import json
            
            # 使用ansible-runner执行playbook
            r = ansible_runner.run(
                playbook=os.path.basename(playbook_path),
                inventory=inventory_file,
                project_dir=os.path.dirname(playbook_path),
                quiet=False,
                extravars={'ansible_host_key_checking': False}
            )
            
            if r.status == 'successful':
                # ansible-runner不直接返回任务数据，需要通过事件流解析
                # 先返回成功状态，后续可以从fact_cache或文件中读取
                return {'success': True, 'runner': r}
            else:
                # 从事件中提取详细的错误信息
                error_msg = self._extract_error_from_events(r)
                if not error_msg:
                    error_msg = f"Playbook failed with status: {r.status}"
                return {'success': False, 'error': error_msg, 'runner': r}
                
        except Exception as e:
            logger.error(f"Error running ansible playbook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _parse_linux_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析Linux采集结果
        从ansible-runner的事件流中提取host_info数据
        
        Args:
            result: ansible执行结果
            
        Returns:
            标准化后的主机信息
        """
        try:
            host_info = {}
            
            # 从runner对象的事件中提取数据
            runner = result.get('runner')
            if runner and hasattr(runner, 'events'):
                for event in runner.events:
                    event_type = event.get('event')
                    event_data = event.get('event_data', {})
                    
                    # 查找set_fact事件，这是存储host_info的地方
                    if event_type in ['runner_on_ok', 'ansible_facts']:
                        # ansible_facts包含收集的事实
                        facts = event_data.get('fact', {})
                        if 'host_info' in facts:
                            host_info.update(facts['host_info'])
                        
                        # 或者从res中查找set_fact
                        res = event_data.get('res', {})
                        if 'ansible_facts' in res and 'host_info' in res['ansible_facts']:
                            host_info.update(res['ansible_facts']['host_info'])
                    
                    # 查找set_fact任务的结果
                    if event_type == 'runner_on_ok':
                        res = event_data.get('res', {})
                        if res.get('ansible_facts', {}).get('host_info'):
                            host_info.update(res['ansible_facts']['host_info'])
            
            return host_info
            
        except Exception as e:
            logger.error(f"Error parsing Linux result: {str(e)}")
            return {}
    
    def _extract_error_from_events(self, runner) -> str:
        """
        从 ansible-runner 的事件中提取详细的错误信息
        
        Args:
            runner: ansible-runner 的 runner 对象
            
        Returns:
            错误信息字符串
        """
        try:
            error_messages = []
            processed_hosts = set()  # 避免重复处理同一主机
            
            if runner and hasattr(runner, 'events'):
                for event in runner.events:
                    event_type = event.get('event')
                    event_data = event.get('event_data', {})
                    host = event_data.get('host', '')
                    
                    # 查找失败和不可达的事件
                    if event_type in ['runner_on_failed', 'runner_on_unreachable']:
                        res = event_data.get('res', {})
                        msg = res.get('msg', '')
                        
                        # 构建主机标识
                        host_key = f"{host}:{event_type}"
                        if host_key in processed_hosts:
                            continue
                        processed_hosts.add(host_key)
                        
                        # 对于 unreachable，提取更详细的信息
                        if event_type == 'runner_on_unreachable':
                            # 提取完整的错误消息
                            if msg:
                                # 提取关键错误信息（如 SSH 连接失败的原因）
                                if 'WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED' in msg:
                                    # 提取 SSH 主机密钥变更的详细信息
                                    lines = msg.split('\n')
                                    key_info = []
                                    for line in lines:
                                        if 'WARNING' in line or 'fingerprint' in line or 'Offending' in line or 'Permission denied' in line:
                                            key_info.append(line.strip())
                                    if key_info:
                                        error_messages.append(f"[{host}] SSH连接失败:\n" + '\n'.join(key_info))
                                    else:
                                        error_messages.append(f"[{host}] {msg}")
                                else:
                                    error_messages.append(f"[{host}] {msg}")
                            else:
                                error_messages.append(f"[{host}] 主机不可达: 无法连接到目标主机")
                        elif event_type == 'runner_on_failed':
                            # 提取失败原因
                            if msg:
                                error_messages.append(f"[{host}] 任务失败: {msg}")
                            else:
                                error_messages.append(f"[{host}] 任务执行失败")
                        
                        # 提取 stderr 中的详细信息
                        if 'stderr' in res and res['stderr']:
                            stderr = res['stderr'].strip()
                            if stderr and stderr not in error_messages:
                                # 只提取关键错误行
                                stderr_lines = stderr.split('\n')
                                for line in stderr_lines:
                                    if any(keyword in line.lower() for keyword in ['error', 'failed', 'denied', 'refused', 'timeout']):
                                        if line.strip() and line.strip() not in error_messages:
                                            error_messages.append(line.strip())
                                        break  # 只取第一行关键错误
            
            # 如果找到了错误信息，合并返回
            if error_messages:
                # 合并所有错误信息，用换行符分隔，最多返回前5条
                return '\n'.join(error_messages[:5])
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting error from events: {str(e)}")
            return ""
    
    def _parse_windows_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析Windows采集结果
        从ansible-runner的事件流中提取host_info数据
        
        Args:
            result: ansible执行结果
            
        Returns:
            标准化后的主机信息
        """
        try:
            host_info = {}
            
            # 从runner对象的事件中提取数据
            runner = result.get('runner')
            if runner and hasattr(runner, 'events'):
                for event in runner.events:
                    event_type = event.get('event')
                    event_data = event.get('event_data', {})
                    
                    # 查找set_fact事件，这是存储host_info的地方
                    if event_type in ['runner_on_ok', 'ansible_facts']:
                        # ansible_facts包含收集的事实
                        facts = event_data.get('fact', {})
                        if 'host_info' in facts:
                            host_info.update(facts['host_info'])
                        
                        # 或者从res中查找set_fact
                        res = event_data.get('res', {})
                        if 'ansible_facts' in res and 'host_info' in res['ansible_facts']:
                            host_info.update(res['ansible_facts']['host_info'])
                    
                    # 查找set_fact任务的结果
                    if event_type == 'runner_on_ok':
                        res = event_data.get('res', {})
                        if res.get('ansible_facts', {}).get('host_info'):
                            host_info.update(res['ansible_facts']['host_info'])
            
            return host_info
            
        except Exception as e:
            logger.error(f"Error parsing Windows result: {str(e)}")
            return {}

