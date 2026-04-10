# config.py
# 集中配置管理
# Centralized Configuration Management

import os
from typing import Optional
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()


class Config:
    """基礎配置類"""
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 伺服器配置
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5050))
    
    # MongoDB 配置
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
    MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
    MONGODB_DB = os.getenv('MONGODB_DB', 'attendance')
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
    
    # MongoDB 連接池配置
    MONGODB_MAX_POOL_SIZE = int(os.getenv('MONGODB_MAX_POOL_SIZE', 50))
    MONGODB_MIN_POOL_SIZE = int(os.getenv('MONGODB_MIN_POOL_SIZE', 10))
    MONGODB_TIMEOUT_MS = int(os.getenv('MONGODB_TIMEOUT_MS', 5000))
    
    # QR Code 配置
    QR_SECRET_KEY = os.getenv('QR_SECRET_KEY')
    if not QR_SECRET_KEY:
        raise ValueError("QR_SECRET_KEY must be set in environment variables")
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Admin token (protect destructive/write APIs)
    # Use header: X-Admin-Token: <token>
    ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')
    
    # 快取配置
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # 速率限制配置
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours
    
    # 分頁配置
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 50))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 500))
    
    # 日誌配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_mongodb_uri(cls) -> str:
        """
        生成 MongoDB 連接 URI
        Generate MongoDB connection URI
        """
        if cls.MONGODB_USERNAME and cls.MONGODB_PASSWORD:
            return (f"mongodb://{cls.MONGODB_USERNAME}:{cls.MONGODB_PASSWORD}@"
                   f"{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/{cls.MONGODB_DB}")
        return f"mongodb://{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/"
    
    @classmethod
    def validate(cls) -> bool:
        """
        驗證配置完整性
        Validate configuration completeness
        """
        required_vars = ['QR_SECRET_KEY']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        # 驗證 QR_SECRET_KEY 長度
        if len(cls.QR_SECRET_KEY) < 32:
            raise ValueError("QR_SECRET_KEY must be at least 32 characters long")
        
        return True


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    FLASK_ENV = 'development'
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    @classmethod
    def validate(cls) -> bool:
        """生產環境需要更嚴格的驗證"""
        super().validate()
        
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be changed in production")
        
        if cls.CORS_ORIGINS == ['*']:
            raise ValueError("CORS_ORIGINS should be restricted in production")

        if not cls.ADMIN_TOKEN:
            raise ValueError("ADMIN_TOKEN must be set in production")

        if len(cls.ADMIN_TOKEN) < 16:
            raise ValueError("ADMIN_TOKEN must be at least 16 characters long")
        
        return True


class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    MONGODB_DB = 'attendance_test'
    RATELIMIT_ENABLED = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}


def get_config(env: Optional[str] = None) -> Config:
    """
    取得配置對象
    Get configuration object
    
    Args:
        env: 環境名稱，如未提供則從 FLASK_ENV 讀取
    
    Returns:
        Config 對象
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'production')
    
    config_class = config.get(env, config['default'])
    config_class.validate()
    
    return config_class
