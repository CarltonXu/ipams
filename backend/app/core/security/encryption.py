"""
凭证加密模块
提供AES对称加密功能用于安全存储凭证信息
"""
import os
from cryptography.fernet import Fernet
from flask import current_app
from app.core.utils.logger import app_logger as logger


def get_encryption_key():
    """
    获取加密密钥
    从环境变量或配置中读取
    """
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        # 如果没有配置，尝试从应用配置获取
        if current_app:
            key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            logger.error("ENCRYPTION_KEY not found in environment or app config")
            raise ValueError("ENCRYPTION_KEY not configured. Please set it in environment variables or app config.")
    
    return key.encode()


def encrypt_credential(plain_text):
    """
    加密凭证信息
    
    Args:
        plain_text (str): 明文
        
    Returns:
        str: 加密后的密文
    """
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted_text = f.encrypt(plain_text.encode())
        return encrypted_text.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise ValueError(f"Failed to encrypt credential: {str(e)}")


def decrypt_credential(encrypted_text):
    """
    解密凭证信息
    
    Args:
        encrypted_text (str): 密文
        
    Returns:
        str: 解密后的明文
    """
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted_text = f.decrypt(encrypted_text.encode())
        return decrypted_text.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        raise ValueError(f"Failed to decrypt credential: {str(e)}")


def generate_encryption_key():
    """
    生成新的加密密钥
    使用 Fernet.generate_key() 生成
    
    Returns:
        str: Base64编码的密钥
    """
    key = Fernet.generate_key()
    return key.decode()


# 测试加密解密功能
if __name__ == "__main__":
    # 生成新密钥
    new_key = generate_encryption_key()
    print(f"Generated encryption key: {new_key}")
    print("\nPlease set this key in your environment variable ENCRYPTION_KEY")

