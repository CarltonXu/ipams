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
                    return self._parse_linux_result(result)
                else:
                    logger.error(f"Failed to collect Linux info from {host_ip}: {result.get('error')}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error collecting Linux info from {host_ip}: {str(e)}")
            return {}
    
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
                    return self._parse_windows_result(result)
                else:
                    logger.error(f"Failed to collect Windows info from {host_ip}: {result.get('error')}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error collecting Windows info from {host_ip}: {str(e)}")
            return {}
    
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

