from app.models import db, NotificationTemplate

def init_notification_templates():
    """初始化通知模板"""
    templates = [
        {
            'name': 'scan_completed',
            'title_template': '扫描任务完成通知',
            'content_template': '扫描任务 {task_name} 已完成。\n扫描范围: {scan_range}\n发现IP数量: {ip_count}',
            'type': 'scan'
        },
        {
            'name': 'scan_failed',
            'title_template': '扫描任务失败通知',
            'content_template': '扫描任务 {task_name} 执行失败。\n错误信息: {error_message}',
            'type': 'scan'
        },
        {
            'name': 'ip_claimed',
            'title_template': 'IP地址认领通知',
            'content_template': 'IP地址 {ip_address} 已被用户 {user_name} 认领。\n认领时间: {claim_time}',
            'type': 'ip'
        },
        {
            'name': 'ip_released',
            'title_template': 'IP地址释放通知',
            'content_template': 'IP地址 {ip_address} 已被用户 {user_name} 释放。\n释放时间: {release_time}',
            'type': 'ip'
        },
        {
            'name': 'policy_created',
            'title_template': '策略创建通知',
            'content_template': '新的扫描策略 {policy_name} 已创建。\n创建者: {creator_name}\n扫描范围: {scan_range}',
            'type': 'policy'
        },
        {
            'name': 'policy_updated',
            'title_template': '策略更新通知',
            'content_template': '扫描策略 {policy_name} 已更新。\n更新者: {updater_name}\n更新内容: {update_content}',
            'type': 'policy'
        },
        {
            'name': 'policy_deleted',
            'title_template': '策略删除通知',
            'content_template': '扫描策略 {policy_name} 已被删除。\n删除者: {deleter_name}',
            'type': 'policy'
        }
    ]

    for template_data in templates:
        template = NotificationTemplate.query.filter_by(name=template_data['name']).first()
        if not template:
            template = NotificationTemplate(**template_data)
            db.session.add(template)
        else:
            for key, value in template_data.items():
                setattr(template, key, value)

    db.session.commit() 