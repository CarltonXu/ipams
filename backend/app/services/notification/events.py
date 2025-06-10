from enum import Enum
from typing import Dict, Any, Optional
from flask import current_app

class NotificationEvent(Enum):
    """通知事件类型"""
    SCAN_COMPLETED = "scan_completed"           # 扫描完成
    SCAN_FAILED = "scan_failed"                # 扫描失败
    IP_CLAIMED = "ip_claimed"                  # IP被认领
    IP_RELEASED = "ip_released"                # IP被释放
    POLICY_CREATED = "policy_created"          # 策略创建
    POLICY_UPDATED = "policy_updated"          # 策略更新
    POLICY_DELETED = "policy_deleted"          # 策略删除
    POLICY_STATUS_UPDATED = "policy_status_updated" # 策略状态更新
    TASK_CANCELLED = "task_cancelled"          # 任务取消
    SYSTEM_ALERT = "system_alert"              # 系统告警

class NotificationTemplate:
    """通知模板"""
    @staticmethod
    def scan_completed(job_name: str, subnet: str, machines_found: int) -> str:
        return f"扫描任务 '{job_name}' 已完成\n" \
               f"目标网段: {subnet}\n" \
               f"发现主机数: {machines_found}"

    @staticmethod
    def scan_failed(job_name: str, subnet: str, error: str) -> str:
        return f"扫描任务 '{job_name}' 失败\n" \
               f"目标网段: {subnet}\n" \
               f"错误信息: {error}"

    @staticmethod
    def ip_claimed(ip: str, user: str) -> str:
        return f"IP地址 {ip} 已被用户 {user} 认领"

    @staticmethod
    def ip_released(ip: str, user: str) -> str:
        return f"IP地址 {ip} 已被用户 {user} 释放"

    @staticmethod
    def policy_created(policy_name: str, user: str) -> str:
        return f"用户 {user} 创建了新的扫描策略 '{policy_name}'"

    @staticmethod
    def policy_updated(policy_name: str, user: str) -> str:
        return f"用户 {user} 更新了扫描策略 '{policy_name}'"

    @staticmethod
    def policy_deleted(policy_name: str, user: str) -> str:
        return f"用户 {user} 删除了扫描策略 '{policy_name}'"
    
    def policy_status_updated(policy_name: str, status: str, user: str) -> str:
        return f"用户 {user} 更新了扫描策略 '{policy_name}'状态为 '{status}'"

    @staticmethod
    def task_cancelled(task_name: str, user: str) -> str:
        return f"用户 {user} 取消了任务 '{task_name}'"

    @staticmethod
    def system_alert(alert_type: str, message: str) -> str:
        return f"系统告警: {alert_type}\n{message}"

def send_notification(
    event: NotificationEvent,
    user: Any,
    template_data: Dict[str, Any],
    additional_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    发送通知
    
    Args:
        event: 通知事件类型
        user: 用户对象
        template_data: 模板数据
        additional_data: 额外数据
    """
    try:
        # 根据事件类型选择模板
        template_method = getattr(NotificationTemplate, event.value)
        message = template_method(**template_data)
        
        # 添加额外信息
        if additional_data:
            message += "\n\n详细信息:\n"
            for key, value in additional_data.items():
                message += f"{key}: {value}\n"
        
        # 发送通知
        current_app.notification_manager.notify_user(user, message)
        
    except Exception as e:
        current_app.notification_manager.app.logger.error(f"Failed to send notification: {str(e)}") 