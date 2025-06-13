#!/bin/bash

# 设置环境变量
export MYSQL_ROOT_PASSWORD="your_root_password"
export MYSQL_PASSWORD="your_password"

# 构建镜像
docker-compose -f ../docker-compose/docker-compose.prod.yml build

# 启动服务
docker-compose -f ../docker-compose/docker-compose.prod.yml up -d

# 等待服务启动
echo "Waiting for services to start..."
sleep 10

# 初始化数据库
docker-compose -f ../docker-compose/docker-compose.prod.yml exec backend flask db upgrade

# 创建初始用户
docker-compose -f ../docker-compose/docker-compose.prod.yml exec backend python create_user.py

echo "Initialization completed!" 