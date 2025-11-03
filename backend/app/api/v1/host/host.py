"""
主机信息管理API
提供主机信息的查询、采集、绑定凭证等功能
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime
import uuid

from app.models.models import db, HostInfo, HostCredentialBinding, CollectionTask, Credential, IP
from app.core.security.auth import token_required
from app.core.utils.logger import app_logger as logger
from app.services.collection.collector_manager import collector_manager
from app.services.export.excel_exporter import excel_exporter


host_bp = Blueprint('host', __name__)


@host_bp.route('/host', methods=['GET'])
@token_required
def get_hosts(current_user):
    """
    获取主机信息列表
    支持分页、搜索和过滤
    自动为已认领的IP创建HostInfo记录（如果不存在）
    """
    try:
        page = request.args.get('page', type=int)
        page_size = request.args.get('page_size', type=int)
        query = request.args.get('query')
        host_type = request.args.get('host_type')
        collection_status = request.args.get('collection_status')
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        
        # 获取当前用户有权限查看的所有IP
        if current_user.is_admin:
            ips_query = IP.query.filter_by(deleted=False, status='active')
        else:
            ips_query = IP.query.filter_by(deleted=False, status='active', assigned_user_id=current_user.id)
        
        # 为每个IP确保存在HostInfo记录
        for ip in ips_query.all():
            host_info = HostInfo.query.filter_by(ip_id=ip.id, deleted=False).first()
            if not host_info:
                # 自动创建HostInfo记录
                host_info = HostInfo(
                    ip_id=ip.id,
                    collection_status='pending'
                )
                db.session.add(host_info)
        
        db.session.commit()
        
        # 构建基础查询
        hosts_query = HostInfo.query.filter_by(deleted=False)
        
        # 只显示当前用户有权限查看的主机
        hosts_query = hosts_query.join(IP).filter(
            or_(
                IP.assigned_user_id == current_user.id,
                current_user.is_admin == True
            )
        )
        
        # 应用搜索条件
        if query:
            hosts_query = hosts_query.filter(
                or_(
                    HostInfo.hostname.ilike(f'%{query}%'),
                    IP.ip_address.ilike(f'%{query}%'),
                    HostInfo.os_name.ilike(f'%{query}%')
                )
            )
        
        # 应用过滤条件
        if host_type and host_type != 'all':
            hosts_query = hosts_query.filter(HostInfo.host_type == host_type)
        
        if collection_status and collection_status != 'all':
            hosts_query = hosts_query.filter(HostInfo.collection_status == collection_status)
        
        # 应用排序
        if sort_by:
            sort_column = getattr(HostInfo, sort_by, None)
            if sort_column is not None:
                hosts_query = hosts_query.order_by(
                    desc(sort_column) if sort_order == 'desc' else asc(sort_column)
                )
        
        # 执行分页查询
        hosts_paginated = hosts_query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )
        
        # 批量加载凭证绑定信息
        host_ids = [h.id for h in hosts_paginated.items]
        bindings_map = {}
        if host_ids:
            bindings = HostCredentialBinding.query.filter(
                HostCredentialBinding.host_id.in_(host_ids)
            ).all()
            for binding in bindings:
                if binding.host_id not in bindings_map:
                    bindings_map[binding.host_id] = []
                bindings_map[binding.host_id].append(binding.to_dict())
        
        # 构建返回数据
        hosts_data = []
        for host in hosts_paginated.items:
            host_dict = host.to_dict()
            host_dict['credential_bindings'] = bindings_map.get(host.id, [])
            hosts_data.append(host_dict)
        
        return jsonify({
            'hosts': hosts_data,
            'total': hosts_paginated.total,
            'pages': hosts_paginated.pages,
            'page_size': page_size,
            'current_page': hosts_paginated.page
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error fetching hosts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/<host_id>', methods=['GET'])
@token_required
def get_host(current_user, host_id):
    """
    获取单个主机详细信息
    """
    try:
        host = HostInfo.query.filter_by(id=host_id, deleted=False).first()
        
        if not host:
            return jsonify({'error': 'Host not found'}), 404
        
        # 检查权限
        if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        return jsonify({
            'host': host.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching host: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/<host_id>', methods=['PUT'])
@token_required
def update_host(current_user, host_id):
    """
    更新主机信息（主要是主机类型）
    """
    try:
        host = HostInfo.query.filter_by(id=host_id, deleted=False).first()
        
        if not host:
            return jsonify({'error': 'Host not found'}), 404
        
        # 检查权限
        if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        # 更新字段
        if 'host_type' in data:
            host.host_type = data['host_type']
        if 'vmware_info' in data:
            host.vmware_info = data['vmware_info']
        
        host.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Host updated successfully',
            'host': host.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating host: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/<host_id>/bind-credential', methods=['POST'])
@token_required
def bind_credential(current_user, host_id):
    """
    绑定凭证到主机
    """
    try:
        host = HostInfo.query.filter_by(id=host_id, deleted=False).first()
        
        if not host:
            return jsonify({'error': 'Host not found'}), 404
        
        # 检查权限
        if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        credential_id = data.get('credential_id')
        
        if not credential_id:
            return jsonify({'error': 'credential_id required'}), 400
        
        # 验证凭证属于当前用户
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        # 检查是否已经绑定
        existing_binding = HostCredentialBinding.query.filter_by(
            host_id=host_id,
            credential_id=credential_id
        ).first()
        
        if existing_binding:
            return jsonify({'error': 'Credential already bound to this host'}), 400
        
        # 创建绑定
        binding = HostCredentialBinding(
            host_id=host_id,
            credential_id=credential_id
        )
        db.session.add(binding)
        db.session.commit()
        
        return jsonify({
            'message': 'Credential bound successfully',
            'binding': binding.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error binding credential: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/<host_id>/unbind-credential', methods=['DELETE'])
@token_required
def unbind_credential(current_user, host_id):
    """
    解绑主机凭证
    """
    try:
        credential_id = request.args.get('credential_id')
        
        if not credential_id:
            return jsonify({'error': 'credential_id required'}), 400
        
        binding = HostCredentialBinding.query.filter_by(
            host_id=host_id,
            credential_id=credential_id
        ).first()
        
        if not binding:
            return jsonify({'error': 'Binding not found'}), 404
        
        # 检查权限
        host = binding.host
        if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(binding)
        db.session.commit()
        
        return jsonify({
            'message': 'Credential unbound successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error unbinding credential: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/<host_id>/collect', methods=['POST'])
@token_required
def collect_host_info(current_user, host_id):
    """
    触发单个主机信息采集
    """
    try:
        host = HostInfo.query.filter_by(id=host_id, deleted=False).first()
        
        if not host:
            return jsonify({'error': 'Host not found'}), 404
        
        # 检查权限
        if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        credential_id = data.get('credential_id')
        
        # 支持自定义凭证
        custom_credential = None
        if data.get('username') or data.get('password'):
            custom_credential = {
                'username': data.get('username'),
                'password': data.get('password'),
                'private_key': data.get('private_key'),
                'credential_type': data.get('credential_type', 'linux'),
                'port': data.get('port')
            }
        
        # 执行采集
        result = collector_manager.collect_single_host(host_id, credential_id, custom_credential)
        
        if result['success']:
            return jsonify({
                'message': 'Collection started successfully',
                'result': result
            }), 200
        else:
            return jsonify({
                'message': 'Collection failed',
                'error': result.get('error')
            }), 500
        
    except Exception as e:
        logger.error(f"Error collecting host info: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/batch-collect', methods=['POST'])
@token_required
def batch_collect_hosts(current_user):
    """
    批量触发主机信息采集
    """
    try:
        data = request.get_json()
        host_ids = data.get('host_ids', [])
        
        if not host_ids:
            return jsonify({'error': 'host_ids required'}), 400
        
        # 创建批量采集任务
        task_id = collector_manager.collect_batch_hosts(host_ids, current_user.id)
        
        return jsonify({
            'message': 'Batch collection started',
            'task_id': task_id
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting batch collection: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/batch-bind', methods=['POST'])
@token_required
def batch_bind_credentials(current_user):
    """
    批量绑定凭证到主机
    """
    try:
        data = request.get_json()
        host_ids = data.get('host_ids', [])
        credential_id = data.get('credential_id')
        
        if not host_ids:
            return jsonify({'error': 'host_ids required'}), 400
        if not credential_id:
            return jsonify({'error': 'credential_id required'}), 400
        
        # 验证凭证属于当前用户
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        bound_count = 0
        skipped_count = 0
        errors = []
        
        for host_id in host_ids:
            try:
                host = HostInfo.query.filter_by(id=host_id, deleted=False).first()
                
                if not host:
                    errors.append(f"Host {host_id}: not found")
                    skipped_count += 1
                    continue
                
                # 检查权限
                if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
                    errors.append(f"Host {host_id}: permission denied")
                    skipped_count += 1
                    continue
                
                # 检查是否已经绑定
                existing = HostCredentialBinding.query.filter_by(
                    host_id=host_id,
                    credential_id=credential_id
                ).first()
                
                if existing:
                    errors.append(f"Host {host_id}: already bound")
                    skipped_count += 1
                    continue
                
                # 创建绑定
                binding = HostCredentialBinding(
                    host_id=host_id,
                    credential_id=credential_id
                )
                db.session.add(binding)
                bound_count += 1
                
            except Exception as e:
                errors.append(f"Host {host_id}: {str(e)}")
                skipped_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Batch bind completed: {bound_count} bound, {skipped_count} skipped',
            'bound_count': bound_count,
            'skipped_count': skipped_count,
            'errors': errors if errors else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error batch binding credentials: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/batch-unbind', methods=['POST'])
@token_required
def batch_unbind_credentials(current_user):
    """
    批量解绑凭证
    """
    try:
        data = request.get_json()
        host_ids = data.get('host_ids', [])
        credential_id = data.get('credential_id')
        
        if not host_ids:
            return jsonify({'error': 'host_ids required'}), 400
        if not credential_id:
            return jsonify({'error': 'credential_id required'}), 400
        
        unbound_count = 0
        skipped_count = 0
        
        for host_id in host_ids:
            binding = HostCredentialBinding.query.filter_by(
                host_id=host_id,
                credential_id=credential_id
            ).first()
            
            if binding:
                # 检查权限
                if not current_user.is_admin and binding.host.ip.assigned_user_id != current_user.id:
                    skipped_count += 1
                    continue
                
                db.session.delete(binding)
                unbound_count += 1
            else:
                skipped_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Batch unbind completed: {unbound_count} unbound, {skipped_count} skipped',
            'unbound_count': unbound_count,
            'skipped_count': skipped_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error batch unbinding credentials: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/<host_id>/collection-history', methods=['GET'])
@token_required
def get_collection_history(current_user, host_id):
    """
    获取主机的采集历史
    """
    try:
        host = HostInfo.query.filter_by(id=host_id, deleted=False).first()
        
        if not host:
            return jsonify({'error': 'Host not found'}), 404
        
        # 检查权限
        if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 返回采集历史和当前状态
        return jsonify({
            'last_collected_at': host.last_collected_at.isoformat() if host.last_collected_at else None,
            'collection_status': host.collection_status,
            'collection_error': host.collection_error
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching collection history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/export', methods=['POST'])
@token_required
def export_hosts(current_user):
    """
    导出主机信息到Excel
    """
    try:
        from flask import send_file
        
        data = request.get_json()
        host_ids = data.get('host_ids', [])
        fields = data.get('fields', [])
        template = data.get('template')
        
        if not host_ids:
            return jsonify({'error': 'host_ids required'}), 400
        
        if not fields and not template:
            return jsonify({'error': 'fields or template required'}), 400
        
        # 获取主机信息
        hosts_query = HostInfo.query.filter(HostInfo.id.in_(host_ids), HostInfo.deleted == False)
        
        # 检查权限
        if not current_user.is_admin:
            hosts_query = hosts_query.join(IP).filter(IP.assigned_user_id == current_user.id)
        
        hosts_list = hosts_query.all()
        hosts_data = [host.to_dict() for host in hosts_list]
        
        # 导出到Excel
        filepath = excel_exporter.export_hosts(hosts_data, fields, template)
        
        # 返回文件
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"hosts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error exporting hosts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/export/templates', methods=['GET'])
@token_required
def get_export_templates(current_user):
    """
    获取导出模板列表
    """
    try:
        templates = excel_exporter.get_template_list()
        return jsonify({'templates': templates}), 200
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/export/fields', methods=['GET'])
@token_required
def get_export_fields(current_user):
    """
    获取可用导出字段列表
    """
    try:
        fields = excel_exporter.get_available_fields()
        return jsonify({'fields': fields}), 200
    except Exception as e:
        logger.error(f"Error fetching fields: {str(e)}")
        return jsonify({'error': str(e)}), 500

