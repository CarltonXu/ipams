"""
凭证管理API
提供凭证的CRUD操作和测试连接功能
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import and_
from datetime import datetime

from app.models.models import db, Credential
from app.core.security.auth import token_required
from app.core.utils.logger import app_logger as logger
from app.core.security.encryption import encrypt_credential, decrypt_credential


credential_bp = Blueprint('credential', __name__)


@credential_bp.route('/credential', methods=['GET'])
@token_required
def get_credentials(current_user):
    """
    获取当前用户的凭证列表
    """
    try:
        credentials = Credential.query.filter_by(
            user_id=current_user.id,
            deleted=False
        ).all()
        
        return jsonify({
            'credentials': [cred.to_dict() for cred in credentials]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching credentials: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential', methods=['POST'])
@token_required
def create_credential(current_user):
    """
    创建新凭证
    """
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'credential_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 加密存储敏感信息
        username = data.get('username')
        password = data.get('password')
        private_key = data.get('private_key')
        
        if username:
            username = encrypt_credential(username)
        if password:
            password = encrypt_credential(password)
        if private_key:
            private_key = encrypt_credential(private_key)
        
        # 创建凭证
        credential = Credential(
            user_id=current_user.id,
            name=data['name'],
            credential_type=data['credential_type'],
            username=username,
            password=password,
            private_key=private_key,
            is_default=data.get('is_default', False)
        )
        
        # 如果设置为默认凭证，取消其他默认凭证
        if credential.is_default:
            Credential.query.filter_by(
                user_id=current_user.id,
                is_default=True,
                deleted=False
            ).update({'is_default': False})
        
        db.session.add(credential)
        db.session.commit()
        
        return jsonify({
            'message': 'Credential created successfully',
            'credential': credential.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating credential: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>', methods=['GET'])
@token_required
def get_credential(current_user, credential_id):
    """
    获取凭证详情（不返回密码明文）
    """
    try:
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        return jsonify({
            'credential': credential.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching credential: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>/detail', methods=['GET'])
@token_required
def get_credential_detail(current_user, credential_id):
    """
    获取凭证详情（包含解密后的用户名密码）
    用于忘记密码时查看凭证信息
    """
    try:
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        # 解密凭证信息
        username = decrypt_credential(credential.username) if credential.username else None
        password = decrypt_credential(credential.password) if credential.password else None
        private_key = decrypt_credential(credential.private_key) if credential.private_key else None
        
        result = credential.to_dict()
        result['username_plain'] = username
        result['password_plain'] = password
        result['private_key_plain'] = private_key
        
        return jsonify({
            'credential': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching credential detail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>/bindings', methods=['GET'])
@token_required
def get_credential_bindings(current_user, credential_id):
    """
    获取凭证绑定的主机列表
    """
    try:
        from app.models.models import HostCredentialBinding, HostInfo, IP
        
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        # 查找绑定的主机
        bindings = HostCredentialBinding.query.filter_by(
            credential_id=credential_id
        ).join(HostInfo).join(IP).all()
        
        # 只返回当前用户有权限查看的主机
        if not current_user.is_admin:
            bindings = [b for b in bindings if b.host.ip.assigned_user_id == current_user.id]
        
        hosts = []
        for binding in bindings:
            host_dict = binding.host.to_dict()
            hosts.append({
                'binding_id': binding.id,
                'host': host_dict,
                'bound_at': binding.created_at.isoformat() if binding.created_at else None
            })
        
        return jsonify({
            'credential_id': credential_id,
            'credential_name': credential.name,
            'total': len(hosts),
            'hosts': hosts
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching credential bindings: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>/batch-bind', methods=['POST'])
@token_required
def batch_bind_hosts(current_user, credential_id):
    """
    批量绑定主机到凭证
    """
    try:
        from app.models.models import HostCredentialBinding, HostInfo, IP
        
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        data = request.get_json()
        host_ids = data.get('host_ids', [])
        
        if not host_ids:
            return jsonify({'error': 'host_ids required'}), 400
        
        bound_count = 0
        skipped_count = 0
        errors = []
        
        for host_id in host_ids:
            try:
                # 检查主机是否存在且权限
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
        logger.error(f"Error batch binding hosts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>/batch-unbind', methods=['POST'])
@token_required
def batch_unbind_hosts(current_user, credential_id):
    """
    批量解绑主机
    """
    try:
        from app.models.models import HostCredentialBinding
        
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        data = request.get_json()
        host_ids = data.get('host_ids', [])
        
        if not host_ids:
            return jsonify({'error': 'host_ids required'}), 400
        
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
        logger.error(f"Error batch unbinding hosts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>', methods=['PUT'])
@token_required
def update_credential(current_user, credential_id):
    """
    更新凭证
    """
    try:
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            credential.name = data['name']
        if 'credential_type' in data:
            credential.credential_type = data['credential_type']
        if 'username' in data:
            credential.username = encrypt_credential(data['username']) if data['username'] else None
        if 'password' in data:
            credential.password = encrypt_credential(data['password']) if data['password'] else None
        if 'private_key' in data:
            credential.private_key = encrypt_credential(data['private_key']) if data['private_key'] else None
        if 'is_default' in data:
            credential.is_default = data['is_default']
            # 如果设置为默认凭证，取消其他默认凭证
            if credential.is_default:
                Credential.query.filter(
                    and_(
                        Credential.user_id == current_user.id,
                        Credential.id != credential_id,
                        Credential.is_default == True,
                        Credential.deleted == False
                    )
                ).update({'is_default': False})
        
        credential.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Credential updated successfully',
            'credential': credential.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating credential: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>', methods=['DELETE'])
@token_required
def delete_credential(current_user, credential_id):
    """
    删除凭证（软删除）
    """
    try:
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        credential.deleted = True
        credential.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Credential deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting credential: {str(e)}")
        return jsonify({'error': str(e)}), 500


@credential_bp.route('/credential/<credential_id>/test', methods=['POST'])
@token_required
def test_credential(current_user, credential_id):
    """
    测试凭证连接
    支持通过host_ip参数指定测试主机
    """
    try:
        credential = Credential.query.filter_by(
            id=credential_id,
            user_id=current_user.id,
            deleted=False
        ).first()
        
        if not credential:
            return jsonify({'error': 'Credential not found'}), 404
        
        # 解密凭证
        username = decrypt_credential(credential.username) if credential.username else None
        password = decrypt_credential(credential.password) if credential.password else None
        private_key = decrypt_credential(credential.private_key) if credential.private_key else None
        
        # 获取测试主机IP
        data = request.get_json() if request.is_json else {}
        host_ip = data.get('host_ip')
        
        # 根据凭证类型测试连接
        result = {'success': False, 'message': ''}
        
        if credential.credential_type == 'linux':
            # 测试SSH连接
            if host_ip:
                result = _test_ssh_connection(host_ip, username, password, private_key)
            else:
                result = {'success': False, 'message': 'host_ip required for Linux connection test'}
        elif credential.credential_type == 'windows':
            # 测试WinRM连接
            if host_ip:
                result = _test_winrm_connection(host_ip, username, password)
            else:
                result = {'success': False, 'message': 'host_ip required for Windows connection test'}
        elif credential.credential_type == 'vmware':
            # 测试VMware连接
            vcenter_host = host_ip or data.get('vcenter_host')
            if vcenter_host:
                result = _test_vmware_connection(vcenter_host, username, password)
            else:
                result = {'success': False, 'message': 'vCenter host required'}
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error testing credential: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


def _test_ssh_connection(host_ip, username, password, private_key):
    """测试SSH连接"""
    try:
        import paramiko
        from io import StringIO
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # 使用私钥或密码连接
            if private_key:
                ssh_key = paramiko.RSAKey.from_private_key(StringIO(private_key))
                if password:
                    ssh.connect(host_ip, username=username, pkey=ssh_key, password=password, timeout=10)
                else:
                    ssh.connect(host_ip, username=username, pkey=ssh_key, timeout=10)
            elif password:
                ssh.connect(host_ip, username=username, password=password, timeout=10)
            else:
                return {'success': False, 'message': 'Either password or private_key required'}
            
            # 执行简单命令验证连接
            stdin, stdout, stderr = ssh.exec_command('echo test', timeout=5)
            exit_status = stdout.channel.recv_exit_status()
            
            ssh.close()
            
            if exit_status == 0:
                return {'success': True, 'message': 'SSH connection successful'}
            else:
                return {'success': False, 'message': f'Command execution failed with exit code {exit_status}'}
                
        except paramiko.AuthenticationException:
            return {'success': False, 'message': 'Authentication failed'}
        except paramiko.SSHException as e:
            return {'success': False, 'message': f'SSH error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}
            
    except ImportError:
        return {'success': False, 'message': 'paramiko library not installed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def _test_winrm_connection(host_ip, username, password):
    """测试WinRM连接"""
    try:
        # WinRM测试需要在Windows环境下使用pywinrm库
        # 这里提供一个简化版本，检查端口是否开放
        import socket
        
        try:
            # 检查5985端口是否开放
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host_ip, 5985))
            sock.close()
            
            if result == 0:
                # 端口开放，尝试使用winrm库测试
                try:
                    import winrm
                    session = winrm.Session(host_ip, auth=(username, password), transport='plaintext')
                    result = session.run_cmd('echo test')
                    if result.status_code == 0:
                        return {'success': True, 'message': 'WinRM connection successful'}
                    else:
                        return {'success': False, 'message': 'WinRM authentication failed'}
                except ImportError:
                    return {
                        'success': False, 
                        'message': 'WinRM port is open but pywinrm library not installed. Install it with: pip install pywinrm'
                    }
                except Exception as e:
                    return {'success': False, 'message': f'WinRM error: {str(e)}'}
            else:
                return {'success': False, 'message': 'WinRM port 5985 is not accessible'}
                
        except socket.error as e:
            return {'success': False, 'message': f'Socket error: {str(e)}'}
            
    except Exception as e:
        return {'success': False, 'message': str(e)}


def _test_vmware_connection(vcenter_host, username, password):
    """测试VMware连接"""
    try:
        from pyVim import connect
        import ssl
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_context.verify_mode = ssl.CERT_NONE
        
        service_instance = connect.SmartConnect(
            host=vcenter_host,
            user=username,
            pwd=password,
            sslContext=ssl_context,
            port=443
        )
        
        connect.Disconnect(service_instance)
        return {'success': True, 'message': 'Connection successful'}
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

