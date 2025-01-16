import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

flask_app = create_app()
celery = flask_app.extensions['celery']

if __name__ == '__main__':
    celery.worker_main(['worker', '--loglevel=info']) 