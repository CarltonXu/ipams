from flask import Blueprint, jsonify, request
from app.core.security.auth import token_required
from app.models.models import db, SystemMetrics, NetworkMetrics, DiskMetrics, ProcessMetrics
from datetime import datetime, timedelta
from sqlalchemy import func

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/monitor', methods=['GET'])
@token_required
def get_monitor_data(current_user):
    """获取各资源独立趋势数据"""
    try:
        # 获取时间范围参数
        time_range = request.args.get('time_range', '1h')
        hours = {
            '1h': 1,
            '6h': 6,
            '24h': 24
        }.get(time_range, 1)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        # CPU/内存趋势（SystemMetrics）
        cpu_metrics = SystemMetrics.query.filter(
            SystemMetrics.timestamp >= start_time,
            SystemMetrics.timestamp <= end_time
        ).order_by(SystemMetrics.timestamp.asc()).all()
        cpu_trend = {
            'timestamps': [m.timestamp.strftime('%Y-%m-%d %H:%M:%S') for m in cpu_metrics],
            'cpu': [m.cpu_usage for m in cpu_metrics]
        }
        memory_trend = {
            'timestamps': [m.timestamp.strftime('%Y-%m-%d %H:%M:%S') for m in cpu_metrics],
            'memory': [m.memory_usage for m in cpu_metrics]
        }

        # 磁盘趋势（DiskMetrics）
        disk_metrics = DiskMetrics.query.filter(
            DiskMetrics.timestamp >= start_time,
            DiskMetrics.timestamp <= end_time
        ).order_by(DiskMetrics.timestamp.asc()).all()
        # 按时间点聚合
        disk_trend_map = {}
        for m in disk_metrics:
            ts = m.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if ts not in disk_trend_map:
                disk_trend_map[ts] = {
                    'read': 0, 'write': 0, 'iops': 0
                }
            disk_trend_map[ts]['read'] += m.read_bytes
            disk_trend_map[ts]['write'] += m.write_bytes
            disk_trend_map[ts]['iops'] += (m.read_count + m.write_count)
        disk_trend = {
            'timestamps': list(disk_trend_map.keys()),
            'disk_read': [v['read'] for v in disk_trend_map.values()],
            'disk_write': [v['write'] for v in disk_trend_map.values()],
            'disk_iops': [v['iops'] for v in disk_trend_map.values()]
        }

        # 网络趋势（NetworkMetrics）
        network_metrics = NetworkMetrics.query.filter(
            NetworkMetrics.timestamp >= start_time,
            NetworkMetrics.timestamp <= end_time
        ).order_by(NetworkMetrics.timestamp.asc()).all()
        network_trend_map = {}
        for m in network_metrics:
            ts = m.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if ts not in network_trend_map:
                network_trend_map[ts] = {'sent': 0, 'recv': 0}
            network_trend_map[ts]['sent'] += m.bytes_sent
            network_trend_map[ts]['recv'] += m.bytes_recv
        network_trend = {
            'timestamps': list(network_trend_map.keys()),
            'network_sent': [v['sent'] for v in network_trend_map.values()],
            'network_recv': [v['recv'] for v in network_trend_map.values()]
        }

        # 最新快照
        latest_metrics = SystemMetrics.get_latest_metrics()
        latest_disk_time = db.session.query(func.max(DiskMetrics.timestamp)).scalar()
        latest_partitions = DiskMetrics.query.filter(DiskMetrics.timestamp == latest_disk_time).all() if latest_disk_time else []
        latest_network_time = db.session.query(func.max(NetworkMetrics.timestamp)).scalar()
        latest_networks = NetworkMetrics.query.filter(NetworkMetrics.timestamp == latest_network_time).all() if latest_network_time else []
        latest_process_time = db.session.query(func.max(ProcessMetrics.timestamp)).scalar()
        latest_processes = ProcessMetrics.query.filter(ProcessMetrics.timestamp == latest_process_time).order_by(ProcessMetrics.cpu_percent.desc()).limit(50).all() if latest_process_time else []

        response_data = {
            'code': 200,
            'data': {
                'cpu_trend': cpu_trend,
                'memory_trend': memory_trend,
                'disk_trend': disk_trend,
                'network_trend': network_trend,
                'stats': {
                    'cpu_usage': latest_metrics.cpu_usage if latest_metrics else 0,
                    'memory_usage': latest_metrics.memory_usage if latest_metrics else 0,
                    'process_count': latest_metrics.process_count if latest_metrics else 0,
                    'cpu_count': latest_metrics.cpu_count if latest_metrics else 0,
                    'memory_total': latest_metrics.memory_total if latest_metrics else 0,
                    'memory_used': latest_metrics.memory_used if latest_metrics else 0,
                    'memory_free': latest_metrics.memory_free if latest_metrics else 0,
                    'load_avg_1min': latest_metrics.load_avg_1min if latest_metrics else 0,
                    'load_avg_5min': latest_metrics.load_avg_5min if latest_metrics else 0,
                    'load_avg_15min': latest_metrics.load_avg_15min if latest_metrics else 0
                },
                'disk': {
                    'partitions': [
                        {
                            'device': m.device,
                            'mountpoint': m.mountpoint,
                            'total': m.total,
                            'used': m.used,
                            'free': m.free,
                            'usage': m.usage,
                            'read_bytes': m.read_bytes,
                            'write_bytes': m.write_bytes,
                            'read_count': m.read_count,
                            'write_count': m.write_count,
                            'read_time': m.read_time,
                            'write_time': m.write_time,
                            'is_removable': m.is_removable,
                            'fstype': m.fstype
                        }
                        for m in latest_partitions
                    ]
                },
                'network': {
                    'interfaces': [
                        {
                            'name': n.interface,
                            'bytes_sent': n.bytes_sent,
                            'bytes_recv': n.bytes_recv,
                            'packets_sent': n.packets_sent,
                            'packets_recv': n.packets_recv,
                            'errin': n.errin,
                            'errout': n.errout,
                            'dropin': n.dropin,
                            'dropout': n.dropout,
                            'is_up': n.is_up,
                            'speed': n.speed,
                            'mtu': n.mtu
                        }
                        for n in latest_networks
                    ]
                },
                'processes': [
                    {
                        'pid': p.pid,
                        'name': p.name,
                        'cpu_percent': p.cpu_percent,
                        'memory_percent': p.memory_percent,
                        'memory_rss': p.memory_rss,
                        'memory_vms': p.memory_vms,
                        'status': p.status,
                        'num_threads': p.num_threads,
                        'create_time': p.create_time.strftime('%Y-%m-%d %H:%M:%S') if p.create_time else None
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