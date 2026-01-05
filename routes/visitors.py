# routes/visitors.py
# 訪客管理路由
# Visitor Management Routes

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
import logging

from database import get_db
from models import VisitorModel
from utils.validators import validate_json, validate_object_id

logger = logging.getLogger(__name__)

# 建立藍圖
visitors_bp = Blueprint('visitors', __name__, url_prefix='/visitors')


@visitors_bp.route('', methods=['GET'])
def get_visitors():
    """
    獲取訪客列表
    Get visitor list
    """
    try:
        db = get_db()
        
        # 取得篩選參數
        search_name = request.args.get('search')
        
        # 建立查詢條件
        query = {}
        if search_name:
            query['name'] = {'$regex': search_name, '$options': 'i'}
        
        visitors = db.visitors.find(query).sort('first_visit_date', -1)
        visitor_list = [VisitorModel.to_dict(v) for v in visitors]
        
        logger.info(f"Retrieved {len(visitor_list)} visitors")
        return jsonify(visitor_list)
        
    except Exception as e:
        logger.error(f"Error retrieving visitors: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@visitors_bp.route('/checkin', methods=['POST'])
@validate_json
def visitor_checkin():
    """
    訪客簽到
    Visitor check-in
    """
    try:
        db = get_db()
        data = request.json
        
        # 驗證資料
        is_valid, error_msg = VisitorModel.validate(data)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        phone = data.get('phone', '').strip()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 檢查是否為回訪（用電話號碼識別）
        visitor = None
        if phone:
            visitor = db.visitors.find_one({'phone': phone})
        
        visitor_id = None
        is_return = False
        
        if visitor:
            # 回訪訪客，更新來訪次數
            visitor_id = str(visitor['_id'])
            db.visitors.update_one(
                {'_id': visitor['_id']},
                {
                    '$inc': {'visit_count': 1},
                    '$set': {
                        'last_visit_date': today,
                        'updated_at': datetime.now().isoformat()
                    }
                }
            )
            is_return = True
            logger.info(f"Returning visitor: {data['name']}, visit count: {visitor['visit_count'] + 1}")
        else:
            # 新訪客 - 修正版：正確插入到 visitors 集合
            new_visitor = VisitorModel.create(data, today)
            result = db.visitors.insert_one(new_visitor)
            visitor_id = str(result.inserted_id)
            logger.info(f"New visitor: {data['name']}")
        
        # 同時建立出勤記錄
        attendance_record = {
            'date': today,
            'name': data['name'].strip(),
            'member_type': 'visitor',
            'visitor_id': visitor_id,
            'session': data.get('session', 'noon'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        db.attendance.insert_one(attendance_record)
        
        return jsonify({
            'message': '訪客簽到成功 / Visitor check-in successful',
            'visitor_id': visitor_id,
            'is_return_visitor': is_return
        }), 201
        
    except Exception as e:
        logger.error(f"Error in visitor check-in: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@visitors_bp.route('/<visitor_id>', methods=['GET'])
def get_visitor(visitor_id):
    """
    獲取單一訪客資料
    Get single visitor
    """
    try:
        db = get_db()
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(visitor_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        visitor = db.visitors.find_one({'_id': ObjectId(visitor_id)})
        if not visitor:
            return jsonify({'error': '訪客不存在 / Visitor not found'}), 404
        
        return jsonify(VisitorModel.to_dict(visitor))
        
    except Exception as e:
        logger.error(f"Error retrieving visitor: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@visitors_bp.route('/<visitor_id>', methods=['PUT'])
@validate_json
def update_visitor(visitor_id):
    """
    更新訪客資料
    Update visitor
    """
    try:
        db = get_db()
        data = request.json
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(visitor_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 驗證資料
        is_valid, error_msg = VisitorModel.validate(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 檢查訪客是否存在
        visitor = db.visitors.find_one({'_id': ObjectId(visitor_id)})
        if not visitor:
            return jsonify({'error': '訪客不存在 / Visitor not found'}), 404
        
        # 更新資料
        update_data = {
            'name': data['name'].strip(),
            'phone': data.get('phone', '').strip(),
            'how_to_know': data.get('how_to_know', '').strip(),
            'updated_at': datetime.now().isoformat()
        }
        
        db.visitors.update_one(
            {'_id': ObjectId(visitor_id)},
            {'$set': update_data}
        )
        
        logger.info(f"Visitor updated: {visitor_id}")
        return jsonify({'message': '訪客資料更新成功 / Visitor updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating visitor: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@visitors_bp.route('/<visitor_id>', methods=['DELETE'])
def delete_visitor(visitor_id):
    """
    刪除訪客
    Delete visitor
    """
    try:
        db = get_db()
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(visitor_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        result = db.visitors.delete_one({'_id': ObjectId(visitor_id)})
        
        if result.deleted_count == 1:
            logger.info(f"Visitor deleted: {visitor_id}")
            return jsonify({'message': '訪客刪除成功 / Visitor deleted successfully'})
        else:
            return jsonify({'error': '訪客不存在 / Visitor not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting visitor: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500
