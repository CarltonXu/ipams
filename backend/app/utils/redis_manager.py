from redis import Redis
from flask import current_app
import logging

class RedisManager:
    @staticmethod
    def get_redis():
        """获取Redis连接"""
        try:
            return current_app.extensions.get('redis')
        except Exception as e:
            logging.error(f"Failed to get Redis connection: {str(e)}")
            return None

    @staticmethod
    def set_with_ttl(key: str, value: str, ttl: int) -> bool:
        """设置带过期时间的键值对"""
        try:
            redis_client = RedisManager.get_redis()
            return redis_client.setex(key, ttl, value)
        except Exception as e:
            logging.error(f"Redis set operation failed: {str(e)}")
            return False

    @staticmethod
    def get(key: str) -> str:
        """获取值"""
        try:
            redis_client = RedisManager.get_redis()
            return redis_client.get(key)
        except Exception as e:
            logging.error(f"Redis get operation failed: {str(e)}")
            return None

    @staticmethod
    def delete(key: str) -> bool:
        """删除键"""
        try:
            redis_client = RedisManager.get_redis()
            return redis_client.delete(key) > 0
        except Exception as e:
            logging.error(f"Redis delete operation failed: {str(e)}")
            return False 