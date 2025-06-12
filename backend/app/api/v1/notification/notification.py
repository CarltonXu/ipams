from flask import Blueprint, jsonify, request, current_app
from app.core.security.auth import token_required
from app.models.models import db, Notification
from app.core.utils.helpers import log_action_to_db
import smtplib # Import smtplib

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notification/config', methods=['GET'])
@token_required
def get_config(current_user):
    """获取通知配置"""
    try:
        configs = current_app.notification_manager.get_all_configs()
        return jsonify(configs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification/config', methods=['PUT'])
@token_required
def update_config(current_user):
    """更新通知配置"""
    try:
        config = request.json
        for key, value in config.items():
            current_app.notification_manager.update_config(current_user.id , key, value)
        return jsonify({'message': '配置更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification/test', methods=['POST'])
@token_required
def test_config(current_user):
    """测试通知配置"""
    try:
        data = request.json
        type = data.get('type')
        config = data.get('config')

        if type == 'email':
            smtp_config = {
                'server': config.get('smtpServer'),
                'username': config.get('smtpUsername'),
                'password': config.get('smtpPassword'),
                'from': config.get('smtpFrom')
            }
            try:
                current_app.notification_manager.email_notifier.send(
                    current_user.email,
                    '这是一条测试通知',
                    smtp_config
                )
                return jsonify({'message': '测试发送成功'}) # Return success here
            except smtplib.SMTPAuthenticationError as e:
                current_app.logger.error(f"Failed to send email notification (Authentication Error): {str(e)}")
                return jsonify({'error': 'SMTP认证失败，请检查用户名和密码。'}), 400
            except smtplib.SMTPException as e:
                current_app.logger.error(f"Failed to send email notification (SMTP Error): {str(e)}")
                return jsonify({'error': '邮件服务器错误：' + str(e)}), 500
            except Exception as e:
                current_app.logger.error(f"Failed to send email notification (General Error): {str(e)}")
                return jsonify({'error': '邮件发送失败：' + str(e)}), 500

        elif type == 'wechat':
            try:
                current_app.notification_manager.wechat_notifier.send(
                    current_user.wechat_id,
                    '这是一条测试通知',
                    config.get('webhookUrl')
                )
                return jsonify({'message': '测试发送成功'}) # Moved this
            except Exception as e:
                current_app.logger.error(f"Failed to send wechat notification: {str(e)}")
                return jsonify({'error': '微信通知发送失败：' + str(e)}), 500

        return jsonify({'error': '无效的通知类型'}), 400 # Handle invalid type
    except Exception as e: # Catch any other unexpected errors
        current_app.logger.error(f"An unexpected error occurred during notification test: {str(e)}")
        return jsonify({'error': '服务器内部错误：' + str(e)}), 500

@notification_bp.route('/notification/history', methods=['GET'])
@token_required
def get_history(current_user):
    """获取通知历史"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        type = request.args.get('type')
        status = request.args.get('status')
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if type:
            query = query.filter_by(type=type)
        if status:
            query = query.filter_by(read=(status == 'read'))
            
        pagination = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page
        )
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in pagination.items],
            'total': pagination.total
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification/<string:id>/read', methods=['PUT'])
@token_required
def mark_as_read(current_user, id):
    """标记通知为已读"""
    try:
        notification = Notification.query.filter_by(id=id, user_id=current_user.id).first()
        if not notification:
            return jsonify({'error': '通知不存在'}), 404
            
        notification.read = True
        db.session.commit()
        return jsonify({'message': '标记已读成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification/read-all', methods=['PUT'])
@token_required
def mark_all_as_read(current_user):
    """标记所有通知为已读"""
    try:
        Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
        db.session.commit()
        return jsonify({'message': '全部标记已读成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification/<string:id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, id):
    """删除通知"""
    try:
        notification = Notification.query.filter_by(id=id, user_id=current_user.id).first()
        if not notification:
            return jsonify({'error': '通知不存在'}), 404
            
        notification.deleted = True
        db.session.commit()
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification/clear-all', methods=['DELETE'])
@token_required
def clear_all(current_user):
    """清空所有通知"""
    try:
        notification = Notification.query.filter_by(user_id=current_user.id).all()
        notification.deleted = True
        db.session.commit()
        return jsonify({'message': '清空成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification/unread-count', methods=['GET'])
@token_required
def get_unread_count(current_user):
    """获取当前用户的未读通知数量"""
    try:
        unread_count = Notification.query.filter_by(user_id=current_user.id, read=False).count()
        return jsonify({'count': unread_count})
    except Exception as e:
        current_app.logger.error(f"获取未读通知数量失败: {str(e)}")
        return jsonify({'error': '获取未读通知数量失败'}), 500 