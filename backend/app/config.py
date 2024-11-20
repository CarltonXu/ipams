import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root123.@127.0.0.1/ipams')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scanner configuration
    NETWORK_RANGE = os.getenv('NETWORK_RANGE', '192.168.0.0/20')
    SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 3600))  # Default: 1 hour
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')