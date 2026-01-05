# routes/health.py
# 健康檢查路由
# Health Check Routes

from flask import Blueprint, jsonify
import logging

from database import db_manager

logger = logging.getLogger(__name__)

# 建立藍圖
health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康檢查端點
    Health check endpoint
    """
    try:
        health_status = db_manager.health_check()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
