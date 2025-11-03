"""
Excel 导出服务
支持自定义字段选择、预设模板、临时文件管理
"""
import os
import tempfile
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import current_app
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

from app.core.utils.logger import app_logger as logger


class ExcelExporter:
    """Excel导出器"""
    
    # 预设模板配置
    TEMPLATES = {
        'basic': {
            'name': '基础信息',
            'fields': ['ip.ip_address', 'hostname', 'host_type', 'os_name', 'collection_status']
        },
        'detailed': {
            'name': '详细信息',
            'fields': [
                'ip.ip_address', 'hostname', 'host_type', 'os_name', 'os_version', 
                'cpu_model', 'cpu_cores', 'memory_total', 'collection_status'
            ]
        },
        'full': {
            'name': '完整信息',
            'fields': [
                'ip.ip_address', 'hostname', 'host_type', 'os_name', 'os_version', 
                'kernel_version', 'cpu_model', 'cpu_cores', 'memory_total',
                'network_interfaces', 'disk_info', 'vmware_info', 'collection_status',
                'last_collected_at', 'collection_error'
            ]
        }
    }
    
    def __init__(self):
        self.export_dir = None
        self.file_expiry = 3600  # 默认1小时过期
    
    def init_app(self, app):
        """初始化应用配置"""
        with app.app_context():
            self.export_dir = app.config.get('EXPORT_FILE_DIR', tempfile.gettempdir())
            self.file_expiry = app.config.get('EXPORT_FILE_EXPIRY', 3600)
            
            # 确保导出目录存在
            os.makedirs(self.export_dir, exist_ok=True)
    
    def export_hosts(self, hosts: List[Dict[str, Any]], fields: List[str], 
                    template: Optional[str] = None) -> str:
        """
        导出主机信息到Excel
        
        Args:
            hosts: 主机信息列表
            fields: 要导出的字段列表
            template: 预设模板名称（可选）
            
        Returns:
            导出文件的路径
        """
        try:
            # 如果有预设模板，使用模板字段
            if template and template in self.TEMPLATES:
                fields = self.TEMPLATES[template]['fields']
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "主机信息"
            
            # 设置表头
            headers = self._get_field_headers(fields)
            ws.append(headers)
            
            # 设置表头样式
            self._style_headers(ws, headers)
            
            # 填充数据
            for host in hosts:
                row_data = self._extract_row_data(host, fields)
                ws.append(row_data)
            
            # 调整列宽
            self._adjust_column_width(ws, headers)
            
            # 保存文件
            filename = f"hosts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(self.export_dir, filename)
            wb.save(filepath)
            
            logger.info(f"Excel export completed: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            raise
    
    def _get_field_headers(self, fields: List[str]) -> List[str]:
        """
        获取字段的显示名称
        
        Args:
            fields: 字段列表
            
        Returns:
            表头列表
        """
        field_names = {
            'ip.ip_address': 'IP地址',
            'hostname': '主机名',
            'host_type': '主机类型',
            'os_name': '操作系统',
            'os_version': '系统版本',
            'kernel_version': '内核版本',
            'cpu_model': 'CPU型号',
            'cpu_cores': 'CPU核心数',
            'memory_total': '总内存(MB)',
            'network_interfaces': '网络接口',
            'disk_info': '磁盘信息',
            'vmware_info': 'VMware信息',
            'collection_status': '采集状态',
            'last_collected_at': '最后采集时间',
            'collection_error': '采集错误'
        }
        
        return [field_names.get(field, field) for field in fields]
    
    def _extract_row_data(self, host: Dict[str, Any], fields: List[str]) -> List[Any]:
        """
        从主机数据中提取行数据
        
        Args:
            host: 主机数据字典
            fields: 字段列表
            
        Returns:
            行数据列表
        """
        row_data = []
        
        for field in fields:
            value = None
            
            # 从host_info或ip中获取值
            if '.' in field:
                # 嵌套字段，如 ip.ip_address
                parts = field.split('.')
                value = host
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = None
                        break
            else:
                value = host.get(field)
            
            # 处理特殊字段
            if field == 'memory_total' and value:
                value = f"{value} MB"
            elif field in ['network_interfaces', 'disk_info', 'vmware_info'] and value:
                # JSON字段转换为字符串
                value = json.dumps(value, ensure_ascii=False)
            elif field == 'collection_status' and value:
                # 状态转换
                status_map = {
                    'pending': '待采集',
                    'collecting': '采集中',
                    'success': '成功',
                    'failed': '失败'
                }
                value = status_map.get(value, value)
            elif field == 'host_type' and value:
                # 主机类型转换
                type_map = {
                    'physical': '物理机',
                    'vmware': 'VMware',
                    'other_virtualization': '其他虚拟化'
                }
                value = type_map.get(value, value)
            elif field == 'last_collected_at' and value:
                # 日期格式化
                if isinstance(value, str):
                    value = value
                else:
                    value = value.isoformat() if hasattr(value, 'isoformat') else str(value)
            
            row_data.append(value)
        
        return row_data
    
    def _style_headers(self, ws, headers: List[str]):
        """
        设置表头样式
        
        Args:
            ws: 工作表对象
            headers: 表头列表
        """
        # 表头样式
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
    
    def _adjust_column_width(self, ws, headers: List[str]):
        """
        调整列宽
        
        Args:
            ws: 工作表对象
            headers: 表头列表
        """
        for col in range(1, len(headers) + 1):
            # 获取最大内容长度
            max_length = len(str(headers[col - 1]))
            
            # 检查当前列的所有单元格
            for row in range(2, ws.max_row + 1):
                cell = ws.cell(row=row, column=col)
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            
            # 设置列宽
            adjusted_width = min(max_length + 2, 50)  # 最大宽度50
            ws.column_dimensions[get_column_letter(col)].width = adjusted_width
    
    def get_available_fields(self) -> List[Dict[str, str]]:
        """
        获取所有可用的导出字段
        
        Returns:
            字段列表，包含字段名和显示名称
        """
        return [
            {'field': 'ip.ip_address', 'label': 'IP地址', 'category': 'basic'},
            {'field': 'hostname', 'label': '主机名', 'category': 'basic'},
            {'field': 'host_type', 'label': '主机类型', 'category': 'basic'},
            {'field': 'os_name', 'label': '操作系统', 'category': 'system'},
            {'field': 'os_version', 'label': '系统版本', 'category': 'system'},
            {'field': 'kernel_version', 'label': '内核版本', 'category': 'system'},
            {'field': 'cpu_model', 'label': 'CPU型号', 'category': 'hardware'},
            {'field': 'cpu_cores', 'label': 'CPU核心数', 'category': 'hardware'},
            {'field': 'memory_total', 'label': '总内存(MB)', 'category': 'hardware'},
            {'field': 'network_interfaces', 'label': '网络接口', 'category': 'network'},
            {'field': 'disk_info', 'label': '磁盘信息', 'category': 'storage'},
            {'field': 'vmware_info', 'label': 'VMware信息', 'category': 'vmware'},
            {'field': 'collection_status', 'label': '采集状态', 'category': 'status'},
            {'field': 'last_collected_at', 'label': '最后采集时间', 'category': 'status'},
            {'field': 'collection_error', 'label': '采集错误', 'category': 'status'}
        ]
    
    def get_template_list(self) -> List[Dict[str, str]]:
        """
        获取预设模板列表
        
        Returns:
            模板列表
        """
        return [
            {
                'id': key,
                'name': value['name'],
                'field_count': len(value['fields'])
            }
            for key, value in self.TEMPLATES.items()
        ]


# 创建全局实例
excel_exporter = ExcelExporter()

