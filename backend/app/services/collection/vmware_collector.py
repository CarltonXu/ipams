"""
VMware 主机信息采集器
使用 pyvmomi 库连接 VMware vCenter/ESXi 并采集虚拟机信息
"""
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import current_app
from app.core.utils.logger import app_logger as logger
from app.core.security.encryption import decrypt_credential


class VMwareCollector:
    """VMware 主机信息采集器"""
    
    def __init__(self):
        pass
    
    def collect_vm_info(self, vcenter_host: str, username: str, password: str, 
                       vm_name: Optional[str] = None, vm_uuid: Optional[str] = None,
                       collect_all_vms: bool = False, 
                       progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
                       max_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        采集VMware虚拟机信息
        
        Args:
            vcenter_host: vCenter/ESXi主机地址
            username: 用户名
            password: 密码
            vm_name: 虚拟机名称（可选）
            vm_uuid: 虚拟机UUID（可选）
            collect_all_vms: 是否采集所有虚拟机（用于vCenter）
            progress_callback: 进度回调函数，参数为(completed, total, vm_info)
            max_workers: 最大并发工作线程数（默认从配置读取）
            
        Returns:
            采集的虚拟机信息字典或列表
        """
        try:
            # 导入pyvmomi相关模块
            from pyVim import connect
            from pyVmomi import vim
            import ssl
            
            # 忽略SSL证书验证
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 连接到vCenter/ESXi
            service_instance = connect.SmartConnect(
                host=vcenter_host,
                user=username,
                pwd=password,
                sslContext=ssl_context,
                port=443
            )
            
            try:
                content = service_instance.RetrieveContent()
                
                # 如果采集所有虚拟机，使用并发采集
                if collect_all_vms:
                    # 获取最大工作线程数
                    if max_workers is None:
                        max_workers = current_app.config.get('VMWARE_COLLECTION_MAX_WORKERS', 10) if current_app else 10
                    
                    vms = self._get_all_vms(content)
                    total = len(vms)
                    
                    logger.info(
                        f"开始VMware采集: vCenter={vcenter_host}, VM数量={total}, 并发线程数={max_workers}",
                        extra={
                            'host_ip': vcenter_host,
                            'vm_count': total,
                            'max_workers': max_workers,
                            'operation': 'vmware_collect_all_start'
                        }
                    )
                    
                    # 使用线程池并发采集
                    vm_list = []
                    completed_count = 0
                    failed_count = 0
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # 提交所有任务
                        future_to_vm = {
                            executor.submit(self._collect_vm_details, vm, content): vm 
                            for vm in vms
                        }
                        
                        # 处理完成的任务
                        for future in as_completed(future_to_vm):
                            vm = future_to_vm[future]
                            try:
                                vm_info = future.result()
                                if vm_info:
                                    vm_list.append(vm_info)
                                    completed_count += 1
                                    # 调用进度回调
                                    if progress_callback:
                                        try:
                                            progress_callback(completed_count, total, vm_info)
                                        except Exception as e:
                                            logger.error(f"Error in progress callback: {str(e)}", exc_info=True)
                                else:
                                    failed_count += 1
                                    logger.warning(
                                        f"Failed to collect VM: {vm.name if hasattr(vm, 'name') else 'Unknown'}"
                                    )
                            except Exception as e:
                                failed_count += 1
                                vm_name = vm.name if hasattr(vm, 'name') else 'Unknown'
                                logger.error(
                                    f"Error collecting VM {vm_name}: {str(e)}",
                                    extra={
                                        'vm_name': vm_name,
                                        'error': str(e),
                                        'operation': 'vmware_collect_single'
                                    }
                                )
                    
                    logger.info(
                        f"VMware采集完成: vCenter={vcenter_host}, 成功={completed_count}, 失败={failed_count}, 总计={total}",
                        extra={
                            'host_ip': vcenter_host,
                            'total_vms': total,
                            'completed': completed_count,
                            'failed': failed_count,
                            'operation': 'vmware_collect_all_complete'
                        }
                    )
                    
                    return {'vms': vm_list, 'total': total, 'completed': completed_count, 'failed': failed_count}
                
                # 查找单个虚拟机
                vm = None
                if vm_uuid:
                    vm = self._get_vm_by_uuid(content, vm_uuid)
                elif vm_name:
                    vm = self._get_vm_by_name(content, vm_name)
                else:
                    logger.error("Either vm_name or vm_uuid must be provided")
                    return {}
                
                if not vm:
                    logger.error(f"VM not found: {vm_name or vm_uuid}")
                    return {}
                
                # 采集虚拟机信息
                vm_info = self._collect_vm_details(vm, content)
                
                return vm_info
                
            finally:
                # 断开连接
                connect.Disconnect(service_instance)
                
        except Exception as e:
            logger.error(f"Error collecting VMware VM info: {str(e)}")
            return {}
    
    def _get_all_vms(self, content):
        """
        获取所有虚拟机
        
        Args:
            content: ServiceContent
            
        Returns:
            虚拟机对象列表
        """
        try:
            from pyVmomi import vim
            
            container = content.rootFolder
            view_type = [vim.VirtualMachine]
            recursive = True
            
            container_view = content.viewManager.CreateContainerView(
                container=container,
                type=view_type,
                recursive=recursive
            )
            
            vms = list(container_view.view)
            container_view.Destroy()
            return vms
            
        except Exception as e:
            logger.error(f"Error getting all VMs: {str(e)}")
            return []
    
    def _get_vm_by_name(self, content, vm_name: str):
        """
        根据名称查找虚拟机
        
        Args:
            content: ServiceContent
            vm_name: 虚拟机名称
            
        Returns:
            虚拟机对象
        """
        try:
            container = content.rootFolder
            view_type = [type(vm_name)] if isinstance(vm_name, str) else [type('')]
            recursive = True
            
            container_view = content.viewManager.CreateContainerView(
                container=container,
                type=view_type,
                recursive=recursive
            )
            
            for managed_object in container_view.view:
                if managed_object.name == vm_name:
                    return managed_object
                    
            container_view.Destroy()
            return None
            
        except Exception as e:
            logger.error(f"Error finding VM by name: {str(e)}")
            return None
    
    def _get_vm_by_uuid(self, content, vm_uuid: str):
        """
        根据UUID查找虚拟机
        
        Args:
            content: ServiceContent
            vm_uuid: 虚拟机UUID
            
        Returns:
            虚拟机对象
        """
        try:
            vm = content.searchIndex.FindByUuid(
                uuid=vm_uuid,
                vmSearch=True,
                instanceUuid=True
            )
            return vm
            
        except Exception as e:
            logger.error(f"Error finding VM by UUID: {str(e)}")
            return None
    
    def _collect_vm_details(self, vm, content) -> Dict[str, Any]:
        """
        采集虚拟机详细信息
        
        Args:
            vm: 虚拟机对象
            content: ServiceContent
            
        Returns:
            虚拟机信息字典
        """
        try:
            # 等待VM信息更新
            import pyVmomi
            while vm.runtime.powerState not in ['poweredOn', 'poweredOff']:
                pass
            
            # 获取摘要信息
            summary = vm.summary
            
            # CPU信息
            cpu_cores = vm.config.hardware.numCPU if hasattr(vm.config, 'hardware') else summary.config.numCpu
            cpu_model = None  # vCenter可能不直接提供CPU型号
            
            # 内存信息
            memory_total = summary.config.memorySizeMB if hasattr(summary.config, 'memorySizeMB') else 0
            
            # Guest OS信息
            guest = summary.guest if hasattr(summary, 'guest') else None
            hostname = guest.hostName if guest and hasattr(guest, 'hostName') else None
            os_name = summary.config.guestFullName if hasattr(summary.config, 'guestFullName') else None
            
            # Guest内存使用情况
            memory_free_mb = None
            if guest and hasattr(guest, 'memoryUsageMB'):
                # 计算空闲内存 = 总内存 - 已使用内存
                memory_used_mb = guest.memoryUsageMB if hasattr(guest, 'memoryUsageMB') else 0
                memory_free_mb = max(0, memory_total - memory_used_mb) if memory_total > 0 else None
            
            # 启动固件类型（BIOS/UEFI）
            boot_method = None
            if hasattr(vm, 'config') and hasattr(vm.config, 'firmware'):
                firmware_type = str(vm.config.firmware) if vm.config.firmware else None
                if firmware_type:
                    if 'efi' in firmware_type.lower() or 'uefi' in firmware_type.lower():
                        boot_method = 'UEFI'
                    elif 'bios' in firmware_type.lower():
                        boot_method = 'BIOS'
                    else:
                        boot_method = firmware_type
            
            # 操作系统位数（从Guest OS信息推断）
            os_bit = None
            if os_name:
                if '64-bit' in os_name or 'x64' in os_name.lower() or 'amd64' in os_name.lower():
                    os_bit = '64-bit'
                elif '32-bit' in os_name or 'x86' in os_name.lower():
                    os_bit = '32-bit'
            
            # 网络接口信息 - 增强：从配置和Guest状态获取详细信息
            network_interfaces = []
            # 从vm.config.hardware.device获取网络适配器配置
            if hasattr(vm, 'config') and hasattr(vm.config, 'hardware') and hasattr(vm.config.hardware, 'device'):
                from pyVmomi import vim
                for device in vm.config.hardware.device:
                    if isinstance(device, vim.vm.device.VirtualEthernetCard):
                        # 获取网络适配器配置信息
                        net_adapter = {
                            'label': device.deviceInfo.label if hasattr(device, 'deviceInfo') else None,
                            'mac_address': device.macAddress if hasattr(device, 'macAddress') else None,
                            'address_type': device.addressType if hasattr(device, 'addressType') else None,
                            'wake_on_lan_enabled': device.wakeOnLanEnabled if hasattr(device, 'wakeOnLanEnabled') else None
                        }
                        
                        # 获取连接的网络名称
                        if hasattr(device, 'backing'):
                            if isinstance(device.backing, vim.vm.device.VirtualEthernetCard.NetworkBackingInfo):
                                net_adapter['network_name'] = device.backing.network.name if device.backing.network else None
                            elif isinstance(device.backing, vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo):
                                net_adapter['portgroup_key'] = device.backing.port.portgroupKey if device.backing.port else None
                        
                        # 从Guest状态获取IP地址信息
                        if guest and hasattr(guest, 'net'):
                            for net in guest.net:
                                if hasattr(net, 'deviceConfigId') and net.deviceConfigId == device.key:
                                    net_adapter['ip_addresses'] = list(net.ipAddress) if hasattr(net, 'ipAddress') and net.ipAddress else []
                                    net_adapter['connected'] = net.connected if hasattr(net, 'connected') else None
                                    net_adapter['network'] = net.network if hasattr(net, 'network') else None
                                    break
                        
                        network_interfaces.append(net_adapter)
            
            # 如果没有从配置获取到网络信息，从Guest状态获取
            if not network_interfaces and guest and hasattr(guest, 'net'):
                for net in guest.net:
                    network_interfaces.append({
                        'device': net.deviceConfigId if hasattr(net, 'deviceConfigId') else None,
                        'ip_addresses': list(net.ipAddress) if hasattr(net, 'ipAddress') and net.ipAddress else [],
                        'mac_address': net.macAddress if hasattr(net, 'macAddress') else None,
                        'connected': net.connected if hasattr(net, 'connected') else None,
                        'network': net.network if hasattr(net, 'network') else None
                    })
            
            # 磁盘信息 - 增强：从配置和Guest状态获取详细信息
            disk_info = []
            # 从vm.config.hardware.device获取虚拟磁盘配置
            if hasattr(vm, 'config') and hasattr(vm.config, 'hardware') and hasattr(vm.config.hardware, 'device'):
                from pyVmomi import vim
                for device in vm.config.hardware.device:
                    if isinstance(device, vim.vm.device.VirtualDisk):
                        disk_detail = {
                            'label': device.deviceInfo.label if hasattr(device, 'deviceInfo') else None,
                            'capacity_bytes': device.capacityInBytes if hasattr(device, 'capacityInBytes') else None,
                            'capacity_kb': device.capacityInKB if hasattr(device, 'capacityInKB') else None,
                            'disk_mode': str(device.backing.diskMode) if hasattr(device, 'backing') and hasattr(device.backing, 'diskMode') else None,
                            'eagerly_scrub': device.backing.eagerlyScrub if hasattr(device, 'backing') and hasattr(device.backing, 'eagerlyScrub') else None,
                            'thin_provisioned': device.backing.thinProvisioned if hasattr(device, 'backing') and hasattr(device.backing, 'thinProvisioned') else None,
                            'uuid': device.backing.uuid if hasattr(device, 'backing') and hasattr(device.backing, 'uuid') else None
                        }
                        
                        # 获取存储路径
                        if hasattr(device, 'backing'):
                            if isinstance(device.backing, vim.vm.device.VirtualDisk.FlatVer2BackingInfo):
                                disk_detail['file_name'] = device.backing.fileName if hasattr(device.backing, 'fileName') else None
                                disk_detail['datastore'] = device.backing.datastore.name if device.backing.datastore else None
                            elif isinstance(device.backing, vim.vm.device.VirtualDisk.SeSparseBackingInfo):
                                disk_detail['file_name'] = device.backing.fileName if hasattr(device.backing, 'fileName') else None
                                disk_detail['datastore'] = device.backing.datastore.name if device.backing.datastore else None
                        
                        # 从Guest状态获取使用情况
                        if hasattr(vm, 'guest') and hasattr(vm.guest, 'disk'):
                            for disk in vm.guest.disk:
                                if hasattr(disk, 'diskPath') and disk.diskPath:
                                    # 尝试匹配磁盘路径
                                    disk_detail['disk_path'] = disk.diskPath
                                    disk_detail['capacity_guest'] = disk.capacity if hasattr(disk, 'capacity') else None
                                    disk_detail['free_space'] = disk.freeSpace if hasattr(disk, 'freeSpace') else None
                                    break
                        
                        disk_info.append(disk_detail)
            
            # 如果没有从配置获取到磁盘信息，从Guest状态获取
            if not disk_info and hasattr(vm, 'guest') and hasattr(vm.guest, 'disk'):
                for disk in vm.guest.disk:
                    disk_info.append({
                        'disk_path': disk.diskPath if hasattr(disk, 'diskPath') else None,
                        'capacity': disk.capacity if hasattr(disk, 'capacity') else None,
                        'free_space': disk.freeSpace if hasattr(disk, 'freeSpace') else None
                    })
            
            # 宿主机信息
            host_info = {}
            if summary.runtime.host:
                host_system = summary.runtime.host
                host_info = {
                    'host_name': host_system.name if hasattr(host_system, 'name') else None,
                    'host_type': 'VMware ESXi'
                }
            
            # 编译信息
            vmware_info = {
                'vm_name': summary.config.name if hasattr(summary.config, 'name') else None,
                'vm_uuid': summary.config.uuid if hasattr(summary.config, 'uuid') else None,
                'power_state': summary.runtime.powerState if hasattr(summary.runtime, 'powerState') else None,
                'tools_status': guest.toolsStatus if guest and hasattr(guest, 'toolsStatus') else None,
                'host': host_info
            }
            
            return {
                'hostname': hostname,
                'os_name': os_name,
                'cpu_model': cpu_model,
                'cpu_cores': cpu_cores,
                'memory_total': memory_total,
                'memory_free_mb': memory_free_mb,
                'os_bit': os_bit,
                'boot_method': boot_method,
                'network_interfaces': network_interfaces,
                'disk_info': disk_info,
                'vmware_info': vmware_info
            }
            
        except Exception as e:
            logger.error(f"Error collecting VM details: {str(e)}")
            return {}

