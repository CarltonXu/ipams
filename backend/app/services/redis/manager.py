from typing import Optional, Any
from redis import Redis
from flask import current_app
import logging
from app.core.error.errors import DatabaseError, DatabaseConnectionError

class RedisManager:
    """Redis 服务管理器"""
    
    @staticmethod
    def get_redis() -> Optional[Redis]:
        """获取 Redis 连接
        
        Returns:
            Optional[Redis]: Redis 客户端实例，如果连接失败则返回 None
            
        Raises:
            DatabaseConnectionError: 当无法获取 Redis 连接时
        """
        try:
            redis_client = current_app.extensions.get('redis')
            if not redis_client:
                raise DatabaseConnectionError("Redis 连接未初始化")
            return redis_client
        except Exception as e:
            logging.error(f"Failed to get Redis connection: {str(e)}")
            raise DatabaseConnectionError(
                message="无法连接到 Redis 服务器",
                details={'original_error': str(e)}
            )

    @staticmethod
    def set_with_ttl(key: str, value: str, ttl: int) -> bool:
        """设置带过期时间的键值对
        
        Args:
            key (str): 键名
            value (str): 值
            ttl (int): 过期时间（秒）
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            DatabaseError: 当 Redis 操作失败时
        """
        try:
            redis_client = RedisManager.get_redis()
            return redis_client.setex(key, ttl, value)
        except Exception as e:
            logging.error(f"Redis set operation failed: {str(e)}")
            raise DatabaseError(
                message="Redis 设置操作失败",
                details={'key': key, 'original_error': str(e)}
            )

    @staticmethod
    def get(key: str) -> Optional[str]:
        """获取值
        
        Args:
            key (str): 键名
            
        Returns:
            Optional[str]: 获取的值，如果键不存在则返回 None
            
        Raises:
            DatabaseError: 当 Redis 操作失败时
        """
        try:
            redis_client = RedisManager.get_redis()
            return redis_client.get(key)
        except Exception as e:
            logging.error(f"Redis get operation failed: {str(e)}")
            raise DatabaseError(
                message="Redis 获取操作失败",
                details={'key': key, 'original_error': str(e)}
            )

    @staticmethod
    def delete(key: str) -> bool:
        """删除键
        
        Args:
            key (str): 要删除的键名
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            DatabaseError: 当 Redis 操作失败时
        """
        try:
            redis_client = RedisManager.get_redis()
            return redis_client.delete(key) > 0
        except Exception as e:
            logging.error(f"Redis delete operation failed: {str(e)}")
            raise DatabaseError(
                message="Redis 删除操作失败",
                details={'key': key, 'original_error': str(e)}
            ) 