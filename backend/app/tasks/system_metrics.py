from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.utils.helpers import get_system_metrics, cleanup_old_metrics
import logging
import threading
import atexit

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

    def __init__(self):
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
                    trigger=IntervalTrigger(seconds=10),
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
            logger.error("Application not initialized")
            return

        try:
            with self._app.app_context():
                metrics = get_system_metrics()
                logger.info("System metrics collected successfully")
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")

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