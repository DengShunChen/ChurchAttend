# app_new.py
# 高榮禮拜堂主日崇拜報到系統 - 重構版後端 API
# Church Attendance System - Refactored Backend API

from flask import Flask
from flask_cors import CORS
import logging
import os

# 導入配置
from config import get_config
from database import db_manager
from utils.logger import setup_logger

# 導入路由藍圖
from routes.attendance import attendance_bp
from routes.members import members_bp
from routes.visitors import visitors_bp
from routes.stats import stats_bp
from routes.sessions import sessions_bp
from routes.health import health_bp

# 取得配置
config = get_config()

# 設定日誌
logger = setup_logger(__name__, level=config.LOG_LEVEL)

def create_app(config_obj=None):
    """
    應用工廠函數
    Application factory function
    """
    # 初始化 Flask 應用
    app = Flask(__name__)
    
    # 載入配置
    if config_obj is None:
        config_obj = config
    
    app.config.from_object(config_obj)
    
    # 設定 CORS
    CORS(app, origins=config_obj.CORS_ORIGINS)
    
    # 連接資料庫
    try:
        db_manager.connect(
            uri=config_obj.get_mongodb_uri(),
            db_name=config_obj.MONGODB_DB,
            max_pool_size=config_obj.MONGODB_MAX_POOL_SIZE,
            min_pool_size=config_obj.MONGODB_MIN_POOL_SIZE,
            timeout_ms=config_obj.MONGODB_TIMEOUT_MS
        )
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    # 註冊藍圖
    app.register_blueprint(health_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(visitors_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(sessions_bp)
    
    logger.info("All blueprints registered")
    
    # 錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return {'error': '找不到該資源 / Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': '伺服器內部錯誤 / Internal server error'}, 500
    
    # 根路由
    @app.route('/')
    def index():
        return {
            'message': '高榮禮拜堂主日崇拜報到系統 API',
            'version': '2.0.0',
            'status': 'running'
        }
    
    # 清理資源
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """應用上下文結束時，不主動關閉連接（由連接池管理）"""
        pass
    
    return app


# 建立應用實例
app = create_app()

if __name__ == '__main__':
    # 開發模式
    # Development mode
    try:
        port = config.PORT
        host = config.HOST
        debug = config.DEBUG
        
        logger.info(f"Starting server on {host}:{port} (debug={debug})")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
    finally:
        # 關閉資料庫連接
        db_manager.disconnect()
