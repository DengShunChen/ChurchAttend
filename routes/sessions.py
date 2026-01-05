# routes/sessions.py
# 場次管理路由
# Session Management Routes

from flask import Blueprint, jsonify
import logging

from models import SessionModel

logger = logging.getLogger(__name__)

# 建立藍圖
sessions_bp = Blueprint('sessions', __name__, url_prefix='/sessions')


@sessions_bp.route('', methods=['GET'])
def get_sessions():
    """
    獲取場次列表
    Get session list
    """
    try:
        sessions = SessionModel.get_all()
        return jsonify(sessions)
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500
