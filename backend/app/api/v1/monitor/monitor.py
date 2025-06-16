from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.core.security.auth import token_required
from app.models.models import db, SystemMetrics, NetworkMetrics, DiskMetrics, ProcessMetrics

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/monitor', methods=['GET'])
@token_required
def get_monitor_data():
    """获取系统监控数据"""
    try:
        # 获取时间范围参数
        time_range = request.args.get('time_range', '1h')
        hours = {
            '1h': 1,
            '6h': 6,
            '24h': 24
        }.get(time_range, 1)

        # 获取最新的系统指标
        latest_metrics = SystemMetrics.get_latest_metrics()
        if not latest_metrics:
            return jsonify({
                'code': 200,
                'data': {
                    'stats': {
                        'cpu_usage': 0,
                        'memory_usage': 0,
                        'disk_usage': 0,
                        'process_count': 0
                    },
                    'resources': {
                        'resource_history': {
                            'timestamps': [],
                            'cpu': [],
                            'memory': [],
                            'disk': [],
                            'network_sent': [],
                            'network_recv': [],
                            'disk_read': [],
                            'disk_write': []
                        }
                    },
                    'processes': []
                }
            })

        # 获取历史数据
        history_metrics = SystemMetrics.get_metrics_history(hours)
        
        # 获取最新的网络指标
        latest_network = NetworkMetrics.query.order_by(NetworkMetrics.timestamp.desc()).first()
        
        # 获取最新的磁盘指标
        latest_disk = DiskMetrics.query.order_by(DiskMetrics.timestamp.desc()).first()
        
        # 获取最新的进程指标
        latest_processes = ProcessMetrics.query.order_by(ProcessMetrics.timestamp.desc()).limit(50).all()

        # 构建响应数据
        response_data = {
            'code': 200,
            'data': {
                'stats': {
                    'cpu_usage': latest_metrics.cpu_usage,
                    'memory_usage': latest_metrics.memory_usage,
                    'disk_usage': latest_disk.usage if latest_disk else 0,
                    'process_count': latest_metrics.process_count
                },
                'resources': {
                    'resource_history': {
                        'timestamps': [m.timestamp.strftime('%Y-%m-%d %H:%M:%S') for m in history_metrics],
                        'cpu': [m.cpu_usage for m in history_metrics],
                        'memory': [m.memory_usage for m in history_metrics],
                        'disk': [m.disk_usage if hasattr(m, 'disk_usage') else 0 for m in history_metrics],
                        'network_sent': [m.bytes_sent if hasattr(m, 'bytes_sent') else 0 for m in history_metrics],
                        'network_recv': [m.bytes_recv if hasattr(m, 'bytes_recv') else 0 for m in history_metrics],
                        'disk_read': [m.read_bytes if hasattr(m, 'read_bytes') else 0 for m in history_metrics],
                        'disk_write': [m.write_bytes if hasattr(m, 'write_bytes') else 0 for m in history_metrics]
                    }
                },
                'processes': [
                    {
                        'pid': p.pid,
                        'name': p.name,
                        'cpu_percent': p.cpu_percent,
                        'memory_percent': p.memory_percent,
                        'status': p.status,
                        'num_threads': p.num_threads
                    }
                    for p in latest_processes
                ]
            }
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取监控数据失败: {str(e)}'
        }), 500 