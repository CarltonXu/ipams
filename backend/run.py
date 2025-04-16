import os
import argparse
from app import create_app
from app.config import get_config

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='IPAMS 后端服务')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                      help='服务器主机地址 (默认: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                      help='服务器端口 (默认: 5000)')
    parser.add_argument('--env', type=str, choices=['development', 'testing', 'production'],
                      default='development', help='运行环境 (默认: development)')
    parser.add_argument('--debug', action='store_true',
                      help='是否启用调试模式')
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = args.env
    
    # 创建应用实例
    app = create_app(get_config())
    
    # 启动服务器
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug if args.debug is not None else app.config['DEBUG']
    )

if __name__ == '__main__':
    main()