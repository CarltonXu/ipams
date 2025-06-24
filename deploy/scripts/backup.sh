#!/bin/bash

# 设置备份目录
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
echo "Backing up database..."
docker-compose -f ../docker-compose.yml exec mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} ipams > $BACKUP_DIR/db_backup_$DATE.sql

# 备份上传文件
echo "Backing up uploads..."
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz ../backend/uploads

# 备份 Redis 数据
echo "Backing up Redis data..."
docker-compose -f ../docker-compose.yml exec redis redis-cli SAVE
docker cp $(docker-compose -f ../docker-compose.yml ps -q redis):/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

echo "Backup completed! Files are stored in $BACKUP_DIR"