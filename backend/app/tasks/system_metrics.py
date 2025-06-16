from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.utils.helpers import get_system_metrics, cleanup_old_metrics
import logging
import threading
import atexit
import psutil
from datetime import datetime
from app.models.models import db, SystemMetrics, NetworkMetrics, DiskMetrics, ProcessMetrics
from app.core.utils.logger import app_logger

logger = logging.getLogger(__name__)

class MetricsScheduler:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _scheduler = None
    _app = None
    _shutdown_registered = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MetricsScheduler, cls).__new__(cls)
        return cls._instance

    def __init__(self, app=None):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    try:
                        if MetricsScheduler._scheduler is None:
                            MetricsScheduler._scheduler = BackgroundScheduler()
                        self.scheduler = MetricsScheduler._scheduler
                        self._initialized = True
                        logger.info("MetricsScheduler initialized")
                    except Exception as e:
                        logger.error(f"Failed to initialize scheduler: {str(e)}")
                        raise

        self._app = app

    def init_app(self, app):
        """初始化应用实例"""
        if not self._app:
            self._app = app
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Metrics scheduler started")
                self.init_scheduler()
                
                # 注册应用退出时的清理函数
                if not self._shutdown_registered:
                    atexit.register(self.shutdown)
                    self._shutdown_registered = True

    def init_scheduler(self):
        """初始化调度器任务"""
        if not self._app:
            logger.error("Application not initialized")
            return

        try:
            with self._lock:
                # 检查是否已经在运行
                existing_jobs = self.scheduler.get_jobs()
                if existing_jobs:
                    logger.info(f"Scheduler already has {len(existing_jobs)} jobs, skipping initialization")
                    return

                # 添加收集指标的任务
                self.scheduler.add_job(
                    self.collect_metrics,
                    trigger=IntervalTrigger(minutes=10),
                    id='collect_metrics',
                    replace_existing=True
                )

                # 添加清理旧数据的任务
                self.scheduler.add_job(
                    self.cleanup_metrics,
                    trigger=IntervalTrigger(days=1),
                    id='cleanup_metrics',
                    replace_existing=True
                )

                logger.info("Initialized metrics scheduler with collection and cleanup jobs")
        except Exception as e:
            logger.error(f"Error initializing scheduler: {str(e)}")

    def collect_metrics(self):
        """收集系统指标"""
        if not self._app:
            app_logger.error("Application not initialized")
            return

        with self._app.app_context():
            try:
                # 收集系统基础指标
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0

                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()

                # 收集系统负载
                load_avg = psutil.getloadavg()

                # 收集进程信息
                process_count = 0
                thread_count = 0
                try:
                    process_count = len(psutil.pids())
                    for proc in psutil.process_iter(['pid', 'num_threads']):
                        try:
                            thread_count += proc.info['num_threads'] or 0
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                except Exception as e:
                    app_logger.error(f"获取线程数时发生错误: {str(e)}")

                # 创建系统指标记录
                system_metrics = SystemMetrics(
                    cpu_usage=cpu_percent,
                    cpu_count=cpu_count,
                    cpu_freq=cpu_freq,
                    memory_total=memory.total,
                    memory_used=memory.used,
                    memory_free=memory.free,
                    memory_usage=memory.percent,
                    swap_total=swap.total,
                    swap_used=swap.used,
                    swap_free=swap.free,
                    load_avg_1min=load_avg[0],
                    load_avg_5min=load_avg[1],
                    load_avg_15min=load_avg[2],
                    process_count=process_count,
                    thread_count=thread_count
                )

                # 收集网络指标
                try:
                    net_io = psutil.net_io_counters()
                    for interface, stats in psutil.net_if_stats().items():
                        if stats.isup:
                            net_metrics = NetworkMetrics(
                                interface=interface,
                                bytes_sent=net_io.bytes_sent,
                                bytes_recv=net_io.bytes_recv,
                                packets_sent=net_io.packets_sent,
                                packets_recv=net_io.packets_recv,
                                errin=net_io.errin,
                                errout=net_io.errout,
                                dropin=net_io.dropin,
                                dropout=net_io.dropout,
                                is_up=True,
                                speed=stats.speed,
                                mtu=stats.mtu
                            )
                            db.session.add(net_metrics)
                except Exception as e:
                    app_logger.error(f"获取网络指标时发生错误: {str(e)}")

                # 收集磁盘指标
                try:
                    for partition in psutil.disk_partitions():
                        if partition.fstype:
                            try:
                                usage = psutil.disk_usage(partition.mountpoint)
                                io_counters = psutil.disk_io_counters(perdisk=True).get(partition.device, None)
                                
                                disk_metrics = DiskMetrics(
                                    device=partition.device,
                                    mountpoint=partition.mountpoint,
                                    total=usage.total,
                                    used=usage.used,
                                    free=usage.free,
                                    usage=usage.percent,
                                    read_bytes=io_counters.read_bytes if io_counters else 0,
                                    write_bytes=io_counters.write_bytes if io_counters else 0,
                                    read_count=io_counters.read_count if io_counters else 0,
                                    write_count=io_counters.write_count if io_counters else 0,
                                    read_time=io_counters.read_time if io_counters else 0,
                                    write_time=io_counters.write_time if io_counters else 0,
                                    is_removable='removable' in partition.opts,
                                    fstype=partition.fstype
                                )
                                db.session.add(disk_metrics)
                            except (PermissionError, OSError) as e:
                                app_logger.warning(f"无法访问磁盘 {partition.mountpoint}: {str(e)}")
                                continue
                except Exception as e:
                    app_logger.error(f"获取磁盘指标时发生错误: {str(e)}")

                # 收集进程指标
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time', 'num_threads']):
                        try:
                            proc_info = proc.info
                            if proc_info['create_time']:
                                create_time = datetime.fromtimestamp(proc_info['create_time'])
                            else:
                                create_time = datetime.now()

                            # 获取进程的 CPU 时间
                            try:
                                cpu_times = proc.cpu_times()
                                cpu_times_user = cpu_times.user
                                cpu_times_system = cpu_times.system
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                cpu_times_user = 0
                                cpu_times_system = 0

                            # 获取进程的内存信息
                            try:
                                memory_info = proc.memory_info()
                                memory_rss = memory_info.rss
                                memory_vms = memory_info.vms
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                memory_rss = 0
                                memory_vms = 0

                            # 获取进程的文件描述符数量
                            try:
                                num_fds = proc.num_fds()
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                                num_fds = 0

                            process_metrics = ProcessMetrics(
                                pid=proc_info['pid'],
                                name=proc_info['name'],
                                cpu_percent=proc_info['cpu_percent'] or 0,  # 如果为 None，使用 0
                                cpu_times_user=cpu_times_user,
                                cpu_times_system=cpu_times_system,
                                memory_percent=proc_info['memory_percent'] or 0,  # 如果为 None，使用 0
                                memory_rss=memory_rss,
                                memory_vms=memory_vms,
                                status=proc_info['status'],
                                create_time=create_time,
                                num_threads=proc_info['num_threads'] or 0,  # 如果为 None，使用 0
                                num_fds=num_fds
                            )
                            db.session.add(process_metrics)
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                            app_logger.debug(f"无法获取进程信息: {str(e)}")
                            continue
                except Exception as e:
                    app_logger.error(f"获取进程指标时发生错误: {str(e)}")

                # 保存所有指标
                db.session.add(system_metrics)
                db.session.commit()
                app_logger.info("System metrics collected successfully")

            except Exception as e:
                db.session.rollback()
                app_logger.error(f"收集系统指标时发生错误: {str(e)}")
                raise

    def cleanup_metrics(self):
        """清理旧数据"""
        if not self._app:
            logger.error("Application not initialized")
            return

        try:
            with self._app.app_context():
                cleanup_old_metrics()
                logger.info("Old metrics cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup metrics: {str(e)}")

    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            try:
                self.scheduler.shutdown(wait=True)
                logger.info("Metrics scheduler stopped")
            except Exception as e:
                logger.error(f"Error shutting down scheduler: {str(e)}")

# 创建全局调度器实例
metrics_scheduler = MetricsScheduler() 