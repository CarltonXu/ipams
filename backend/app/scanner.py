import nmap
from datetime import datetime
from .models import db, IP
from apscheduler.schedulers.background import BackgroundScheduler

# 使用 nmap.PortScanner()
nm = nmap.PortScanner()

def scan_network(app, network_range):
    with app.app_context():
        try:
            # 执行网络扫描
            results = nm.scan(hosts=network_range, arguments='-sn')  # '-sn' 用于仅进行 Ping 扫描
            # 处理扫描结果
            scanned_ips = set()
            for host in results['scan']:
                if 'hostnames' in results['scan'][host]:
                    ip_address = host
                    scanned_ips.add(ip_address)
                    
                    # 更新或创建 IP 记录
                    ip = IP.query.filter_by(ip_address=ip_address).first()
                    if ip:
                        ip.last_scanned = datetime.utcnow()
                        if ip.status == 'inactive':
                            ip.status = 'unclaimed'
                    else:
                        ip = IP(
                            ip_address=ip_address,
                            status='unclaimed',
                            last_scanned=datetime.utcnow()
                        )
                        db.session.add(ip)
            
            # 标记未响应的 IP 为 inactive
            IP.query.filter(
                IP.ip_address.notin_(scanned_ips),
                IP.status != 'inactive'
            ).update({
                'status': 'inactive',
                'last_scanned': datetime.utcnow()
            }, synchronize_session=False)
            
            db.session.commit()
            
        except Exception as e:
            app.logger.error(f"Error during network scan: {str(e)}")

def setup_scanner(app):
    scheduler = BackgroundScheduler()
    network_range = app.config['NETWORK_RANGE']
    scan_interval = app.config['SCAN_INTERVAL']
    
    # 定期扫描
    scheduler.add_job(
        func=scan_network,
        args=[app, network_range],
        trigger='interval',
        seconds=scan_interval,
        id='network_scanner'
    )
    
    # 启动调度器
    scheduler.start()
    
    # 执行初次扫描
    scan_network(app, network_range)