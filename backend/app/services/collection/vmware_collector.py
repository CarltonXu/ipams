"""
VMware 主机信息采集器
使用 pyvmomi 库连接 VMware vCenter/ESXi 并采集虚拟机信息
"""
from typing import Dict, Any, Optional
from flask import current_app
from app.core.utils.logger import app_logger as logger
from app.core.security.encryption import decrypt_credential


class VMwareCollector:
    """VMware 主机信息采集器"""
    
    def __init__(self):
        pass
    
    def collect_vm_info(self, vcenter_host: str, username: str, password: str, 
                       vm_name: Optional[str] = None, vm_uuid: Optional[str] = None,
                       collect_all_vms: bool = False) -> Dict[str, Any]:
        """
        采集VMware虚拟机信息
        
        Args:
            vcenter_host: vCenter/ESXi主机地址
            username: 用户名
            password: 密码
            vm_name: 虚拟机名称（可选）
            vm_uuid: 虚拟机UUID（可选）
            collect_all_vms: 是否采集所有虚拟机（用于vCenter）
            
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
                
                # 如果采集所有虚拟机
                if collect_all_vms:
                    vms = self._get_all_vms(content)
                    vm_list = []
                    for vm in vms:
                        vm_info = self._collect_vm_details(vm, content)
                        vm_list.append(vm_info)
                    return {'vms': vm_list, 'total': len(vm_list)}
                
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
                'network_interfaces': network_interfaces,
                'disk_info': disk_info,
                'vmware_info': vmware_info
            }
            
        except Exception as e:
            logger.error(f"Error collecting VM details: {str(e)}")
            return {}

