"""
主机信息管理API
提供主机信息的查询、采集、绑定凭证等功能
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import joinedload
from datetime import datetime
import uuid

from app.models.models import db, HostInfo, HostCredentialBinding, CollectionTask, Credential, IP, CollectionProgress
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
        
        # 优化：批量确保存在HostInfo记录，避免N+1查询
        # 使用子查询找出没有HostInfo的IP，然后批量创建
        if current_user.is_admin:
            ip_filter = and_(IP.deleted == False, IP.status == 'active')
        else:
            ip_filter = and_(IP.deleted == False, IP.status == 'active', IP.assigned_user_id == current_user.id)
        
        # 找出没有HostInfo的IP（使用LEFT JOIN）
        ips_without_hostinfo = db.session.query(IP.id).filter(ip_filter).outerjoin(
            HostInfo, and_(
                HostInfo.ip_id == IP.id,
                HostInfo.deleted == False
            )
        ).filter(HostInfo.id.is_(None)).all()
        
        # 批量创建缺失的HostInfo记录
        if ips_without_hostinfo:
            new_hostinfos = [
                HostInfo(
                    ip_id=ip_id[0],
                    collection_status='pending'
                )
                for ip_id in ips_without_hostinfo
            ]
            db.session.bulk_save_objects(new_hostinfos)
            db.session.commit()
        
        # 构建基础查询（只查询根主机，不包括子主机）
        # 使用 eager loading 优化关联查询，避免懒加载造成的N+1问题
        hosts_query = HostInfo.query.filter_by(deleted=False, parent_host_id=None)
        
        # 判断是否需要JOIN IP表（用于搜索或权限过滤）
        needs_ip_join = False
        if query:  # 如果搜索条件包含IP地址，需要JOIN
            needs_ip_join = True
        if not current_user.is_admin:  # 非管理员需要权限过滤
            needs_ip_join = True
        
        if needs_ip_join:
            hosts_query = hosts_query.join(IP)
            if not current_user.is_admin:
                hosts_query = hosts_query.filter(IP.assigned_user_id == current_user.id)
        else:
            # 即使不需要JOIN，也要预加载IP关系
            hosts_query = hosts_query.options(joinedload(HostInfo.ip))
        
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
        
        # 批量加载凭证绑定信息（优化：使用eager loading避免N+1查询）
        host_ids = [h.id for h in hosts_paginated.items]
        bindings_map = {}
        if host_ids:
            bindings = HostCredentialBinding.query.filter(
                HostCredentialBinding.host_id.in_(host_ids)
            ).options(
                joinedload(HostCredentialBinding.credential)  # 预加载凭证信息
            ).all()
            for binding in bindings:
                if binding.host_id not in bindings_map:
                    bindings_map[binding.host_id] = []
                bindings_map[binding.host_id].append(binding.to_dict())
        
        # 构建返回数据（支持树形结构）
        # 优化：批量加载子主机，避免递归查询中的N+1问题
        child_hosts_map = {}
        if host_ids:
            # 一次性加载所有子主机
            child_hosts = HostInfo.query.filter(
                HostInfo.parent_host_id.in_(host_ids),
                HostInfo.deleted == False
            ).options(joinedload(HostInfo.ip)).all()
            for child in child_hosts:
                if child.parent_host_id not in child_hosts_map:
                    child_hosts_map[child.parent_host_id] = []
                child_hosts_map[child.parent_host_id].append(child)
        
        hosts_data = []
        for host in hosts_paginated.items:
            # 使用预加载的子主机数据，避免递归查询
            host_dict = host.to_dict(include_children=False)
            # 手动添加子主机数据
            if host.id in child_hosts_map:
                host_dict['child_hosts'] = [
                    child.to_dict(include_children=False) 
                    for child in child_hosts_map[host.id]
                ]
            else:
                host_dict['child_hosts'] = []
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
    触发单个主机信息采集（改为异步批量采集方式以支持进度显示）
    """
    try:
        host = HostInfo.query.filter_by(id=host_id, deleted=False).first()
        
        if not host:
            return jsonify({'error': 'Host not found'}), 404
        
        # 检查权限
        if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 使用批量采集API来处理单个主机，这样可以支持进度显示
        task_id = collector_manager.collect_batch_hosts([host_id], current_user.id)
        
        return jsonify({
            'message': 'Collection started successfully',
            'task_id': task_id
        }), 202  # 202 Accepted 表示请求已接受，正在处理
        
    except Exception as e:
        logger.error(f"Error starting collection: {str(e)}")
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
    支持导出父主机及其所有子主机
    """
    try:
        from flask import send_file
        
        data = request.get_json()
        host_ids = data.get('host_ids', [])
        fields = data.get('fields', [])
        template = data.get('template')
        include_children = data.get('include_children', True)  # 默认包含子主机
        
        if not host_ids:
            return jsonify({'error': 'host_ids required'}), 400
        
        if not fields and not template:
            return jsonify({'error': 'fields or template required'}), 400
        
        # 获取主机信息
        hosts_query = HostInfo.query.filter(HostInfo.id.in_(host_ids), HostInfo.deleted == False)
        
        # 检查权限
        if not current_user.is_admin:
            hosts_query = hosts_query.join(IP).filter(IP.assigned_user_id == current_user.id)
        
        hosts_list = hosts_query.options(joinedload(HostInfo.ip)).all()
        
        # 如果需要包含子主机，递归查找所有子主机
        all_host_ids = set(host_ids)
        if include_children:
            # 一次性加载所有可能的子主机，避免递归查询
            all_child_hosts = HostInfo.query.filter(
                HostInfo.parent_host_id.isnot(None),
                HostInfo.deleted == False
            ).options(joinedload(HostInfo.ip)).all()
            
            # 构建父主机ID到子主机的映射
            parent_to_children = {}
            for child in all_child_hosts:
                parent_id = child.parent_host_id
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(child)
            
            # 递归查找所有子主机ID（包括子主机的子主机）
            def find_all_children_recursive(parent_ids, visited=None):
                """递归查找所有子主机ID"""
                if visited is None:
                    visited = set()
                if not parent_ids:
                    return set(), []
                
                child_ids = set()
                child_objects = []
                
                for parent_id in parent_ids:
                    if parent_id in visited:
                        continue
                    visited.add(parent_id)
                    
                    if parent_id in parent_to_children:
                        for child in parent_to_children[parent_id]:
                            child_ids.add(child.id)
                            child_objects.append(child)
                            # 递归查找子主机的子主机
                            grandchild_ids, grandchild_objects = find_all_children_recursive([child.id], visited)
                            child_ids.update(grandchild_ids)
                            child_objects.extend(grandchild_objects)
                
                return child_ids, child_objects
            
            child_ids, child_hosts = find_all_children_recursive(host_ids)
            all_host_ids.update(child_ids)
            
            # 添加子主机到列表
            if child_hosts:
                hosts_list.extend(child_hosts)
        
        # 构建父主机信息映射（优化：避免在循环中查询数据库）
        parent_host_info_map = {}
        all_parent_ids = set()
        for host in hosts_list:
            if host.parent_host_id:
                all_parent_ids.add(host.parent_host_id)
        
        if all_parent_ids:
            # 一次性查询所有父主机信息
            parent_hosts = HostInfo.query.filter(
                HostInfo.id.in_(list(all_parent_ids))
            ).options(joinedload(HostInfo.ip)).all()
            for parent in parent_hosts:
                parent_host_info_map[parent.id] = {
                    'hostname': parent.hostname,
                    'ip_address': parent.ip.ip_address if parent.ip else ''
                }
        
        # 转换为字典格式
        hosts_data = []
        for host in hosts_list:
            host_dict = host.to_dict(include_children=False)
            # 添加父主机信息标识（用于Excel中标识层级关系）
            if host.parent_host_id and host.parent_host_id in parent_host_info_map:
                parent_info = parent_host_info_map[host.parent_host_id]
                host_dict['_parent_hostname'] = parent_info['hostname'] or parent_info['ip_address']
            hosts_data.append(host_dict)
        
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


@host_bp.route('/host/collection-progress/<task_id>', methods=['GET'])
@token_required
def get_collection_progress(current_user, task_id):
    """
    获取采集任务进度
    
    Args:
        task_id: 采集任务ID或CollectionTask ID
    """
    try:
        # 首先尝试从CollectionProgress表中查找
        progress = CollectionProgress.query.filter_by(task_id=task_id).first()
        
        if progress:
            # 检查权限：确保任务属于当前用户
            task = CollectionTask.query.get(task_id)
            if task and task.user_id != current_user.id and not current_user.is_admin:
                return jsonify({'error': 'Permission denied'}), 403
            
            return jsonify(progress.to_dict()), 200
        
        # 如果没有CollectionProgress记录，尝试从CollectionTask获取基本信息
        task = CollectionTask.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # 检查权限
        if task.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 计算进度百分比
        progress_percent = 0
        if task.total_hosts > 0:
            completed = task.success_count + task.failed_count
            progress_percent = round((completed / task.total_hosts) * 100, 2)
        
        # 尝试从 CollectionProgress 获取详细错误信息（如果有）
        progress_detail = CollectionProgress.query.filter_by(task_id=task_id).first()
        error_message = None
        if progress_detail and progress_detail.error_message:
            error_message = progress_detail.error_message
        
        return jsonify({
            'task_id': task.id,
            'total_count': task.total_hosts,
            'completed_count': task.success_count + task.failed_count,
            'success_count': task.success_count,
            'failed_count': task.failed_count,
            'status': task.status,
            'current_step': f"Processing hosts ({task.success_count + task.failed_count}/{task.total_hosts})",
            'progress_percent': progress_percent,
            'error_message': error_message,  # 添加错误信息字段
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.end_time.isoformat() if task.end_time else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching collection progress: {str(e)}")
        return jsonify({'error': str(e)}), 500


@host_bp.route('/host/collection-tasks', methods=['GET'])
@token_required
def get_collection_tasks(current_user):
    """
    获取当前用户的采集任务列表
    支持分页和状态过滤
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status')  # pending, running, completed, failed
        
        # 构建查询
        query = CollectionTask.query.filter_by(user_id=current_user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        # 按创建时间倒序
        query = query.order_by(desc(CollectionTask.created_at))
        
        # 分页
        paginated = query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )
        
        tasks_data = []
        for task in paginated.items:
            # 获取进度信息（如果有）
            progress = CollectionProgress.query.filter_by(task_id=task.id).first()
            
            task_dict = task.to_dict()
            if progress:
                task_dict['progress'] = progress.to_dict()
            
            tasks_data.append(task_dict)
        
        return jsonify({
            'tasks': tasks_data,
            'total': paginated.total,
            'pages': paginated.pages,
            'page_size': page_size,
            'current_page': paginated.page
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching collection tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

