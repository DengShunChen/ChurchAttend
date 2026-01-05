# routes/attendance.py
# 出勤管理路由
# Attendance Management Routes

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
import logging

from database import get_db
from models import AttendanceModel
from utils.validators import validate_json, validate_object_id, validate_pagination, sanitize_string

logger = logging.getLogger(__name__)

# 建立藍圖
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('', methods=['GET'])
def get_attendances():
    """
    獲取出勤記錄（支援分頁和篩選）
    Get attendance records (with pagination and filtering)
    """
    try:
        db = get_db()
        
        # 取得查詢參數
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search_name = request.args.get('search', '').strip()
        session = request.args.get('session')
        member_type = request.args.get('member_type')
        
        # 分頁參數
        page = request.args.get('page', 1)
        page_size = request.args.get('page_size', 50)
        
        # 驗證分頁
        is_valid, error_msg, page, page_size = validate_pagination(page, page_size)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 建立查詢條件
        query = {}
        
        # 日期篩選
        if date_from and date_to:
            query['date'] = {'$gte': date_from, '$lte': date_to}
        elif date_from:
            query['date'] = date_from
        
        # 姓名搜尋（模糊比對）
        if search_name:
            query['name'] = {'$regex': sanitize_string(search_name), '$options': 'i'}
        
        # 場次篩選
        if session:
            query['session'] = session
        
        # 會友/訪客篩選
        if member_type:
            query['member_type'] = member_type

        # 會友 ID 篩選 (Member ID filtering)
        member_id = request.args.get('member_id')
        if member_id:
            query['member_id'] = member_id
        
        # 計算總數
        total_count = db.attendance.count_documents(query)
        
        # 計算跳過的記錄數
        skip = (page - 1) * page_size
        
        # 查詢資料
        attendances = db.attendance.find(query).sort('date', -1).skip(skip).limit(page_size)
        
        attendance_list = [AttendanceModel.to_dict(att) for att in attendances]
        
        logger.info(f"Retrieved {len(attendance_list)} attendance records (page {page}, total {total_count})")
        
        return jsonify({
            'data': attendance_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total_count,
                'pages': (total_count + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving attendances: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@attendance_bp.route('', methods=['POST'])
@validate_json
def create_attendance():
    """
    新增出勤記錄
    Create attendance record
    """
    try:
        db = get_db()
        data = request.json
        
        # 驗證資料
        is_valid, error_msg = AttendanceModel.validate(data)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        date = data['date']
        name = sanitize_string(data['name'])
        
        # 檢查重複報到
        existing = db.attendance.find_one({
            'date': date,
            'name': name
        })
        
        if existing:
            logger.warning(f"Duplicate attendance attempt: {name} on {date}")
            return jsonify({
                'error': f'{name} 已經在 {date} 報到過了 / {name} has already checked in on {date}'
            }), 409
        
        # 建立新記錄
        new_attendance = AttendanceModel.create(data)
        
        result = db.attendance.insert_one(new_attendance)
        logger.info(f"New attendance added: {name} on {date}, ID: {result.inserted_id}")

        # Update member's last_attended_date if it's a member
        # 如果是會友，更新最後出席日期
        if data.get('member_id'):
             db.members.update_one(
                {'_id': ObjectId(data['member_id'])},
                {'$set': {'last_attended_date': date}}
            )
        # Verify if we can find member by name if member_id is missing (optional but good for manual entry)
        elif name:
             # Try to find member by name to update last_attended_date
             # 嘗試用姓名尋找會友並更新
             member = db.members.find_one({'name': name})
             if member:
                 db.members.update_one(
                    {'_id': member['_id']},
                    {'$set': {'last_attended_date': date}}
                )
        
        return jsonify({
            'message': '報到成功 / Attendance added successfully',
            'id': str(result.inserted_id),
            'data': AttendanceModel.to_dict({**new_attendance, '_id': result.inserted_id})
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating attendance: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@attendance_bp.route('/<attendance_id>', methods=['DELETE'])
def delete_attendance(attendance_id):
    """
    刪除出勤記錄
    Delete attendance record
    """
    try:
        db = get_db()
        
        # 驗證 ObjectId 格式
        is_valid, error_msg = validate_object_id(attendance_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        result = db.attendance.delete_one({'_id': ObjectId(attendance_id)})
        
        if result.deleted_count == 1:
            logger.info(f"Attendance deleted: ID {attendance_id}")
            return jsonify({'message': '刪除成功 / Attendance deleted successfully'})
        else:
            logger.warning(f"Failed to delete attendance: ID {attendance_id}")
            return jsonify({'error': '刪除失敗，找不到該記錄 / Failed to delete, record not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting attendance: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@attendance_bp.route('/scan', methods=['POST'])
@validate_json
def qr_scan_checkin():
    """
    QR Code 掃描簽到
    QR code scan check-in
    """
    try:
        db = get_db()
        data = request.json
        
        if not data.get('qr_data'):
            return jsonify({'error': 'QR Code 資料為必填 / QR code data is required'}), 400
        
        # 驗證並解密 QR Code
        import qr_utils
        is_valid, member_data = qr_utils.validate_qr_scan(data['qr_data'])
        
        if not is_valid:
            return jsonify({'error': '無效的 QR Code / Invalid QR code'}), 400
        
        # 取得日期和場次
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        session = data.get('session', 'noon')
        
        # 檢查重複報到
        existing = db.attendance.find_one({
            'date': date,
            'member_id': member_data['id']
        })
        
        if existing:
            return jsonify({
                'error': f"{member_data['name']} 已經在 {date} 報到過了 / Already checked in on {date}"
            }), 409
        
        # 新增簽到記錄
        new_attendance = {
            'date': date,
            'name': member_data['name'],
            'member_type': 'member',
            'member_id': member_data['id'],
            'session': session,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = db.attendance.insert_one(new_attendance)
        
        # Update member's last_attended_date
        # 更新會友最後出席日期
        db.members.update_one(
            {'_id': ObjectId(member_data['id'])},
            {'$set': {'last_attended_date': date}}
        )

        logger.info(f"QR scan check-in: {member_data['name']} on {date}, session: {session}")
        
        return jsonify({
            'message': f"{member_data['name']} 簽到成功！ / Check-in successful!",
            'name': member_data['name'],
            'date': date,
            'session': session,
            'id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        logger.error(f"Error in QR scan check-in: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500
