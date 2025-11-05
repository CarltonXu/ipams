"""
主机信息管理API
提供主机信息的查询、采集、绑定凭证等功能
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import joinedload
from datetime import datetime
import uuid
import time

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
    注意：HostInfo记录应在IP认领时自动创建，这里不再进行全表扫描检查
    """
    try:
        # 性能监控：记录开始时间
        start_time = time.time()
        perf_log = {}
        
        page = request.args.get('page', type=int)
        page_size = request.args.get('page_size', type=int)
        query = request.args.get('query')
        host_type = request.args.get('host_type')
        collection_status = request.args.get('collection_status')
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        # 性能优化：是否计算总数（默认计算，但可以通过参数跳过以提高性能）
        include_count = request.args.get('include_count', 'true').lower() == 'true'
        
        # 构建基础查询（只查询根主机，不包括子主机）
        # 使用 eager loading 优化关联查询，避免懒加载造成的N+1问题
        hosts_query = HostInfo.query.filter_by(deleted=False, parent_host_id=None)
        
        # 判断是否需要JOIN IP表（用于搜索或权限过滤）
        needs_ip_join = False
        if query:  # 如果搜索条件包含IP地址，需要JOIN
            needs_ip_join = True
        if not current_user.is_admin:  # 非管理员需要权限过滤
            needs_ip_join = True
        if host_type and host_type != 'all':  # 如果过滤host_type，可能需要JOIN来访问IP.host_type
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
            # 如果HostInfo.host_type为空，则使用IP.host_type作为fallback
            # needs_ip_join已经在上面判断时包含了host_type的情况
            hosts_query = hosts_query.filter(
                or_(
                    HostInfo.host_type == host_type,
                    and_(
                        HostInfo.host_type.is_(None),
                        IP.host_type == host_type
                    )
                )
            )
        
        if collection_status and collection_status != 'all':
            hosts_query = hosts_query.filter(HostInfo.collection_status == collection_status)
        
        # 应用排序
        if sort_by:
            sort_column = getattr(HostInfo, sort_by, None)
            if sort_column is not None:
                hosts_query = hosts_query.order_by(
                    desc(sort_column) if sort_order == 'desc' else asc(sort_column)
                )
        
        # 确保page和page_size有默认值
        page = page if page and page > 0 else 1
        page_size = page_size if page_size and page_size > 0 else 10
        offset = (page - 1) * page_size
        limit = page_size
        
        # 执行查询，只获取当前页的数据
        query_start = time.time()
        hosts_list = hosts_query.offset(offset).limit(limit).all()
        perf_log['main_query'] = round((time.time() - query_start) * 1000, 2)  # 毫秒
        
        # 批量加载凭证绑定信息（优化：使用eager loading避免N+1查询）
        host_ids = [h.id for h in hosts_list]
        bindings_map = {}
        if host_ids:
            bindings_start = time.time()
            bindings = HostCredentialBinding.query.filter(
                HostCredentialBinding.host_id.in_(host_ids)
            ).options(
                joinedload(HostCredentialBinding.credential)  # 预加载凭证信息
            ).all()
            perf_log['bindings_query'] = round((time.time() - bindings_start) * 1000, 2)
            for binding in bindings:
                if binding.host_id not in bindings_map:
                    bindings_map[binding.host_id] = []
                # 简化to_dict，只返回必要字段
                bindings_map[binding.host_id].append({
                    'id': binding.id,
                    'host_id': binding.host_id,
                    'credential_id': binding.credential_id,
                    'created_at': binding.created_at.isoformat() if binding.created_at else None,
                    'credential': {
                        'id': binding.credential.id if binding.credential else None,
                        'name': binding.credential.name if binding.credential else None,
                        'credential_type': binding.credential.credential_type if binding.credential else None,
                        'username': binding.credential.username if binding.credential else None
                    } if binding.credential else None
                })
        
        # 构建返回数据（支持树形结构）
        # 优化：批量加载子主机，避免递归查询中的N+1问题
        child_hosts_map = {}
        if host_ids:
            child_start = time.time()
            # 一次性加载所有子主机
            child_hosts = HostInfo.query.filter(
                HostInfo.parent_host_id.in_(host_ids),
                HostInfo.deleted == False
            ).options(joinedload(HostInfo.ip)).all()
            perf_log['child_hosts_query'] = round((time.time() - child_start) * 1000, 2)
            for child in child_hosts:
                if child.parent_host_id not in child_hosts_map:
                    child_hosts_map[child.parent_host_id] = []
                child_hosts_map[child.parent_host_id].append(child)
        
        # 优化序列化：手动构建字典，避免嵌套的to_dict调用
        serialize_start = time.time()
        hosts_data = []
        for host in hosts_list:
            # 手动构建host_dict，避免多次to_dict调用
            host_dict = {
                'id': host.id,
                'ip_id': host.ip_id,
                'host_type': host.host_type,
                'hostname': host.hostname,
                'os_name': host.os_name,
                'os_version': host.os_version,
                'cpu_model': host.cpu_model,
                'cpu_cores': host.cpu_cores,
                'memory_total': host.memory_total,
                'collection_status': host.collection_status,
                'collection_error': host.collection_error,
                'last_collected_at': host.last_collected_at.isoformat() if host.last_collected_at else None,
                'created_at': host.created_at.isoformat() if host.created_at else None,
                'updated_at': host.updated_at.isoformat() if host.updated_at else None,
            }
            
            # 添加IP信息（简化版，避免嵌套to_dict）
            if host.ip:
                host_dict['ip'] = {
                    'id': host.ip.id,
                    'ip_address': host.ip.ip_address,
                    'status': host.ip.status,
                    'device_name': host.ip.device_name,
                    'os_type': host.ip.os_type,
                    'host_type': host.ip.host_type,
                    'assigned_user_id': host.ip.assigned_user_id
                }
            else:
                host_dict['ip'] = None
            
            # 手动添加子主机数据（简化版）
            if host.id in child_hosts_map:
                host_dict['child_hosts'] = [
                    {
                        'id': child.id,
                        'ip_id': child.ip_id,
                        'host_type': child.host_type,
                        'hostname': child.hostname,
                        'collection_status': child.collection_status,
                        'ip': {
                            'id': child.ip.id,
                            'ip_address': child.ip.ip_address,
                            'host_type': child.ip.host_type,
                            'os_type': child.ip.os_type
                        } if child.ip else None
                    }
                    for child in child_hosts_map[host.id]
                ]
            else:
                host_dict['child_hosts'] = []
            
            host_dict['credential_bindings'] = bindings_map.get(host.id, [])
            hosts_data.append(host_dict)
        perf_log['serialization'] = round((time.time() - serialize_start) * 1000, 2)
        
        # 优化COUNT查询：如果include_count为false，跳过COUNT查询以提高性能
        if include_count and page:
            count_start = time.time()
            # 使用子查询优化COUNT，避免重复执行复杂的JOIN和过滤
            count_query = db.session.query(func.count(HostInfo.id)).filter_by(deleted=False, parent_host_id=None)
            
            # 应用相同的过滤条件（但不需要JOIN所有数据）
            if needs_ip_join:
                count_query = count_query.join(IP)
                if not current_user.is_admin:
                    count_query = count_query.filter(IP.assigned_user_id == current_user.id)
            
            if query:
                if not needs_ip_join:
                    count_query = count_query.join(IP)
                count_query = count_query.filter(
                    or_(
                        HostInfo.hostname.ilike(f'%{query}%'),
                        IP.ip_address.ilike(f'%{query}%'),
                        HostInfo.os_name.ilike(f'%{query}%')
                    )
                )
            
            if host_type and host_type != 'all':
                if not needs_ip_join:
                    count_query = count_query.join(IP)
                count_query = count_query.filter(
                    or_(
                        HostInfo.host_type == host_type,
                        and_(
                            HostInfo.host_type.is_(None),
                            IP.host_type == host_type
                        )
                    )
                )
            
            if collection_status and collection_status != 'all':
                count_query = count_query.filter(HostInfo.collection_status == collection_status)
            
            total_count = count_query.scalar()
            total_pages = (total_count + page_size - 1) // page_size
            perf_log['count_query'] = round((time.time() - count_start) * 1000, 2)
        else:
            total_count = None if not include_count else len(hosts_list)
            total_pages = None if not include_count else 1
            perf_log['count_query'] = 0  # 跳过了COUNT查询
        
        # 记录总耗时
        total_time = round((time.time() - start_time) * 1000, 2)
        perf_log['total'] = total_time
        
        # 性能日志（仅在开发环境或慢查询时记录）
        if total_time > 1000:  # 超过1秒记录警告
            logger.warning(f"Slow query detected: {perf_log} | params: page={page}, page_size={page_size}, query={query}, host_type={host_type}, collection_status={collection_status}")
        elif total_time > 500:  # 超过500ms记录信息
            logger.info(f"Query performance: {perf_log} | params: page={page}, page_size={page_size}")
        
        return jsonify({
            'hosts': hosts_data,
            'total': total_count,
            'pages': total_pages,
            'page_size': page_size,
            'current_page': page,
            'performance': perf_log if request.args.get('debug') == 'true' else None  # 仅在debug模式下返回性能数据
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
        
        # 检查是否是VMware子主机，子主机不能绑定凭证
        if host.parent_host_id:
            return jsonify({
                'error': 'Cannot bind credential to VMware child host. Child hosts use parent host credentials for collection.'
            }), 400
        
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
        
        # 根据IP的host_type和os_type验证凭证类型
        ip = host.ip
        if ip:
            ip_host_type = ip.host_type
            ip_os_type = ip.os_type
            
            # 验证规则
            if ip_host_type == 'vmware':
                if credential.credential_type != 'vmware':
                    return jsonify({
                        'error': f'VMware hosts can only bind vmware credentials. Selected credential type: {credential.credential_type}'
                    }), 400
            elif ip_host_type in ['physical', 'other_virtualization']:
                if ip_os_type == 'Linux' and credential.credential_type != 'linux':
                    return jsonify({
                        'error': f'Linux hosts can only bind linux credentials. Selected credential type: {credential.credential_type}'
                    }), 400
                elif ip_os_type == 'Windows' and credential.credential_type != 'windows':
                    return jsonify({
                        'error': f'Windows hosts can only bind windows credentials. Selected credential type: {credential.credential_type}'
                    }), 400
        
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
        
        # 立即更新主机状态为'collecting'，防止重复点击
        host.collection_status = 'collecting'
        db.session.commit()
        
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
        
        # 立即批量更新所有主机状态为'collecting'，防止重复点击
        hosts = HostInfo.query.filter(HostInfo.id.in_(host_ids), HostInfo.deleted == False).all()
        for host in hosts:
            # 检查权限
            if current_user.is_admin or (host.ip and host.ip.assigned_user_id == current_user.id):
                host.collection_status = 'collecting'
        db.session.commit()
        
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
                
                # 检查是否是VMware子主机，子主机不能绑定凭证
                if host.parent_host_id:
                    errors.append(f"Host {host_id}: Cannot bind credential to VMware child host. Child hosts use parent host credentials for collection.")
                    skipped_count += 1
                    continue
                
                # 检查权限
                if not current_user.is_admin and host.ip.assigned_user_id != current_user.id:
                    errors.append(f"Host {host_id}: permission denied")
                    skipped_count += 1
                    continue
                
                # 根据IP的host_type和os_type验证凭证类型
                ip = host.ip
                if ip:
                    ip_host_type = ip.host_type
                    ip_os_type = ip.os_type
                    
                    # 验证规则
                    if ip_host_type == 'vmware':
                        if credential.credential_type != 'vmware':
                            errors.append(f"Host {host_id}: VMware hosts can only bind vmware credentials. Selected credential type: {credential.credential_type}")
                            skipped_count += 1
                            continue
                    elif ip_host_type in ['physical', 'other_virtualization']:
                        if ip_os_type == 'Linux' and credential.credential_type != 'linux':
                            errors.append(f"Host {host_id}: Linux hosts can only bind linux credentials. Selected credential type: {credential.credential_type}")
                            skipped_count += 1
                            continue
                        elif ip_os_type == 'Windows' and credential.credential_type != 'windows':
                            errors.append(f"Host {host_id}: Windows hosts can only bind windows credentials. Selected credential type: {credential.credential_type}")
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
    支持分页、状态过滤和按主机ID过滤
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status')  # pending, running, completed, failed
        host_id = request.args.get('host_id')  # 按主机ID过滤
        
        # 构建查询
        query = CollectionTask.query.filter_by(user_id=current_user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        # 如果指定了host_id，需要通过CollectionProgress关联查询
        if host_id:
            # 查找包含该主机的任务
            # 方法1：通过CollectionProgress查询（更准确）
            progress_with_host = CollectionProgress.query.filter_by(host_id=host_id).all()
            task_ids_from_progress = [p.task_id for p in progress_with_host]
            
            # 方法2：如果指定了状态过滤，且是pending或running，通过时间窗口查找最近的任务
            # 这可以处理任务刚创建但CollectionProgress还没创建的情况
            task_ids_from_time = []
            if status in ['pending', 'running'] or not status:
                from datetime import timedelta
                # 查找最近5分钟内创建的任务
                time_threshold = datetime.utcnow() - timedelta(minutes=5)
                recent_tasks = CollectionTask.query.filter(
                    CollectionTask.user_id == current_user.id,
                    CollectionTask.created_at >= time_threshold,
                    CollectionTask.status.in_(['pending', 'running'])
                ).all()
                
                # 检查这些任务是否包含该主机（通过查询CollectionProgress或通过时间推断）
                for task in recent_tasks:
                    # 检查是否有该主机的进度记录
                    host_progress = CollectionProgress.query.filter_by(
                        task_id=task.id,
                        host_id=host_id
                    ).first()
                    if host_progress:
                        task_ids_from_time.append(task.id)
                    # 如果没有进度记录，但任务状态匹配且时间很近，也可能包含该主机
                    # 这种情况下，如果任务状态是pending且是最近创建的，很可能包含该主机
                    elif task.status == 'pending' and task.created_at >= datetime.utcnow() - timedelta(minutes=1):
                        # 通过查询主机是否有对应的状态变化来推断
                        # 如果主机状态是collecting且最后更新时间在任务创建时间附近，可能是该任务
                        host_info = HostInfo.query.get(host_id)
                        if host_info and host_info.collection_status == 'collecting':
                            task_ids_from_time.append(task.id)
            
            # 合并两种方法找到的任务ID
            all_task_ids = list(set(task_ids_from_progress + task_ids_from_time))
            
            if all_task_ids:
                query = query.filter(CollectionTask.id.in_(all_task_ids))
            else:
                # 如果没有找到相关任务，返回空结果
                return jsonify({
                    'tasks': [],
                    'total': 0,
                    'pages': 0,
                    'page_size': page_size,
                    'current_page': page
                }), 200
        
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
            
            # 获取该任务关联的所有主机信息
            # 方法1：通过CollectionProgress查询所有相关的主机
            progress_records = CollectionProgress.query.filter_by(task_id=task.id).all()
            host_ids_from_progress = set()
            for p in progress_records:
                if p.host_id:
                    host_ids_from_progress.add(p.host_id)
            
            # 方法2：如果任务已完成，可以通过查询最近采集的主机来推断
            # 但更可靠的方法是：在任务创建时记录主机ID列表
            # 为了兼容现有数据，我们通过查询该任务创建时间附近、状态为collecting/success/failed的主机
            # 但这个方法不够准确，所以我们优先使用方法1
            
            # 如果从progress中获取到主机ID，查询主机信息
            related_hosts = []
            if host_ids_from_progress:
                hosts = HostInfo.query.filter(
                    HostInfo.id.in_(list(host_ids_from_progress)),
                    HostInfo.deleted == False
                ).options(joinedload(HostInfo.ip)).all()
                
                for host in hosts:
                    related_hosts.append({
                        'id': host.id,
                        'hostname': host.hostname,
                        'ip_address': host.ip.ip_address if host.ip else None,
                        'host_type': host.host_type,
                        'collection_status': host.collection_status,
                        'collection_error': host.collection_error
                    })
            
            # 如果从progress中没有获取到主机ID（可能是旧数据），尝试通过时间推断
            # 查询任务创建时间前后1分钟内，状态发生变化的主机
            if not related_hosts and task.created_at:
                from datetime import timedelta
                time_window_start = task.created_at - timedelta(minutes=1)
                time_window_end = task.created_at + timedelta(minutes=5)
                
                # 查询该时间窗口内最后采集的主机（通过last_collected_at）
                inferred_hosts = HostInfo.query.filter(
                    HostInfo.last_collected_at.between(time_window_start, time_window_end),
                    HostInfo.deleted == False
                ).options(joinedload(HostInfo.ip)).limit(task.total_hosts).all()
                
                for host in inferred_hosts:
                    related_hosts.append({
                        'id': host.id,
                        'hostname': host.hostname,
                        'ip_address': host.ip.ip_address if host.ip else None,
                        'host_type': host.host_type,
                        'collection_status': host.collection_status,
                        'collection_error': host.collection_error
                    })
            
            task_dict['related_hosts'] = related_hosts
            
            # 如果指定了host_id过滤，只保留匹配的主机
            if host_id:
                task_dict['related_hosts'] = [h for h in related_hosts if h['id'] == host_id]
                if task_dict['related_hosts']:
                    task_dict['related_host'] = task_dict['related_hosts'][0]  # 保持向后兼容
            
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


@host_bp.route('/host/collection-task/<task_id>/cancel', methods=['POST'])
@token_required
def cancel_collection_task(current_user, task_id):
    """
    取消采集任务
    
    Args:
        task_id: 采集任务ID
    """
    try:
        # 验证任务存在
        task = CollectionTask.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # 检查权限
        if task.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 只能取消待处理或运行中的任务
        if task.status not in ['pending', 'running']:
            return jsonify({
                'error': f'Cannot cancel task with status: {task.status}',
                'current_status': task.status
            }), 400
        
        # 调用采集管理器取消任务
        success = collector_manager.cancel_collection_task(task_id, current_user.id)
        
        if success:
            return jsonify({
                'message': 'Task cancelled successfully',
                'task_id': task_id
            }), 200
        else:
            return jsonify({'error': 'Failed to cancel task'}), 500
        
    except Exception as e:
        logger.error(f"Error cancelling collection task: {str(e)}")
        return jsonify({'error': str(e)}), 500

