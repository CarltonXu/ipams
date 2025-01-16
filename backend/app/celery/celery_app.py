from celery import Celery

celery = Celery('backend')  # 创建 celery 实例

def init_celery(app):
    celery.conf.update(
        broker_url=f'redis://{app.config.get("REDIS_HOST")}:{app.config.get("REDIS_PORT")}/0',
        result_backend=f'redis://{app.config.get("REDIS_HOST")}:{app.config.get("REDIS_PORT")}/1',
        broker_connection_retry=True,
        broker_connection_max_retries=0,
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery