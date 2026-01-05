# routes/members.py
# 會友管理路由
# Member Management Routes

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
import logging

from database import get_db
from models import MemberModel
from utils.validators import validate_json, validate_object_id
import qr_utils
import csv
import io

logger = logging.getLogger(__name__)

# 建立藍圖
members_bp = Blueprint('members', __name__, url_prefix='/members')


@members_bp.route('', methods=['GET'])
def get_members():
    """
    獲取會友列表
    Get member list
    """
    try:
        db = get_db()
        
        # 取得篩選參數
        group = request.args.get('group')
        search_name = request.args.get('search')
        
        # 建立查詢條件
        query = {}
        if group:
            query['group'] = group
        if search_name:
            query['name'] = {'$regex': search_name, '$options': 'i'}
        
        members = db.members.find(query).sort('name', 1)
        member_list = [MemberModel.to_dict(m) for m in members]
        
        logger.info(f"Retrieved {len(member_list)} members")
        return jsonify(member_list)
        
    except Exception as e:
        logger.error(f"Error retrieving members: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@members_bp.route('', methods=['POST'])
@validate_json
def create_member():
    """
    新增會友
    Create member
    """
    try:
        db = get_db()
        data = request.json
        
        # 驗證資料
        is_valid, error_msg = MemberModel.validate(data)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # 檢查是否已存在
        existing = db.members.find_one({'name': data['name']})
        if existing:
            return jsonify({'error': '會友已存在 / Member already exists'}), 409
        
        # 生成 QR Code
        member_id = str(ObjectId())
        qr_result = qr_utils.generate_member_qr_code(member_id, data['name'])
        
        new_member = MemberModel.create(data, qr_result['qr_data'])
        new_member['_id'] = ObjectId(member_id)
        
        db.members.insert_one(new_member)
        logger.info(f"New member added: {data['name']}, ID: {member_id}")
        
        return jsonify({
            'message': '會友新增成功 / Member added successfully',
            'member_id': member_id,
            'qr_image': qr_result['qr_image'],
            'data': MemberModel.to_dict(new_member)
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating member: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@members_bp.route('/<member_id>', methods=['GET'])
def get_member(member_id):
    """
    獲取單一會友資料
    Get single member
    """
    try:
        db = get_db()
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(member_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        member = db.members.find_one({'_id': ObjectId(member_id)})
        if not member:
            return jsonify({'error': '會友不存在 / Member not found'}), 404
        
        return jsonify(MemberModel.to_dict(member))
        
    except Exception as e:
        logger.error(f"Error retrieving member: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@members_bp.route('/<member_id>', methods=['PUT'])
@validate_json
def update_member(member_id):
    """
    更新會友資料
    Update member
    """
    try:
        db = get_db()
        data = request.json
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(member_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 驗證資料
        is_valid, error_msg = MemberModel.validate(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 檢查會友是否存在
        member = db.members.find_one({'_id': ObjectId(member_id)})
        if not member:
            return jsonify({'error': '會友不存在 / Member not found'}), 404
        
        # 更新資料
        update_data = {
            'name': data['name'].strip(),
            'phone': data.get('phone', '').strip(),
            'group': data.get('group', '').strip(),
            'birthday': data.get('birthday', '').strip(),
            'address': data.get('address', '').strip(),
            'email': data.get('email', '').strip(),
            'line_id': data.get('line_id', '').strip(),
            'updated_at': datetime.now().isoformat()
        }
        
        db.members.update_one(
            {'_id': ObjectId(member_id)},
            {'$set': update_data}
        )
        
        logger.info(f"Member updated: {member_id}")
        return jsonify({'message': '會友資料更新成功 / Member updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating member: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@members_bp.route('/<member_id>/notes', methods=['POST'])
@validate_json
def add_shepherding_note(member_id):
    """
    新增牧養日誌
    Add shepherding note
    """
    try:
        db = get_db()
        data = request.json
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(member_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 驗證會友是否存在
        member = db.members.find_one({'_id': ObjectId(member_id)})
        if not member:
            return jsonify({'error': '會友不存在 / Member not found'}), 404
        
        # 驗證筆記內容
        content = data.get('content')
        if not content:
            return jsonify({'error': '筆記內容為必填 / Note content is required'}), 400
            
        note = {
            'id': str(ObjectId()),
            'date': datetime.now().isoformat(),
            'content': content.strip(),
            'category': data.get('category', 'general'), # general, visit, prayer
            'author': data.get('author', 'admin') # In future, replace with logged-in user
        }
        
        db.members.update_one(
            {'_id': ObjectId(member_id)},
            {'$push': {'shepherding_notes': note}}
        )
        
        logger.info(f"Note added to member: {member_id}")
        return jsonify({'message': '牧養日誌新增成功 / Shepherding note added', 'note': note})
        
    except Exception as e:
        logger.error(f"Error adding note: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@members_bp.route('/<member_id>', methods=['DELETE'])
def delete_member(member_id):
    """
    刪除會友
    Delete member
    """
    try:
        db = get_db()
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(member_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        result = db.members.delete_one({'_id': ObjectId(member_id)})
        
        if result.deleted_count == 1:
            logger.info(f"Member deleted: {member_id}")
            return jsonify({'message': '會友刪除成功 / Member deleted successfully'})
        else:
            return jsonify({'error': '會友不存在 / Member not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting member: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@members_bp.route('/<member_id>/qrcode', methods=['GET'])
def get_member_qrcode(member_id):
    """
    獲取會友 QR Code
    Get member QR code
    """
    try:
        db = get_db()
        
        # 驗證 ObjectId
        is_valid, error_msg = validate_object_id(member_id)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        member = db.members.find_one({'_id': ObjectId(member_id)})
        if not member:
            return jsonify({'error': '會友不存在 / Member not found'}), 404
        
        # 重新生成 QR Code 圖片（資料從資料庫讀取）
        qr_result = qr_utils.generate_qr_image(member['qr_data'])
        
        return jsonify({
            'member_id': member_id,
            'name': member['name'],
            'qr_image': qr_result,
            'qr_data': member['qr_data']
        })
        
    except Exception as e:
        logger.error(f"Error getting member QR code: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@members_bp.route('/import', methods=['POST'])
def import_members_from_csv():
    """
    從 CSV 匯入會友
    Import members from CSV
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': '沒有上傳檔案 / No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未選擇檔案 / No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': '只支援 CSV 檔案 / Only CSV files are supported'}), 400

        # Read CSV content
        # Use utf-8-sig to handle BOM automatically
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        csv_input = csv.DictReader(stream)
        
        # Check Expected Header
        if not csv_input.fieldnames:
             return jsonify({'error': 'CSV 檔案是空的 / Empty CSV file'}), 400
             
        results = {
            "total": 0,
            "inserted": 0,
            "skipped": 0,
            "errors": []
        }
        
        db = get_db()
        
        for row in csv_input:
            results["total"] += 1
            
            # Simple normalization for key access
            row_lower = {k.lower(): v for k, v in row.items() if k}
            
            # Extract fields
            name = row_lower.get('name')
            if not name:
                results["errors"].append(f"Row {results['total']}: Missing Name")
                continue
            
            name = name.strip()
            phone = row_lower.get('phone', '').strip()
            group = row_lower.get('group', '').strip()
            
            # Check duplicate
            existing = db.members.find_one({'name': name})
            if existing:
                results["skipped"] += 1
                continue
                
            # Create Member
            try:
                data = {
                    'name': name,
                    'phone': phone,
                    'group': group
                }
                
                # Validation
                is_valid, error_msg = MemberModel.validate(data)
                if not is_valid:
                     results["errors"].append(f"Row {results['total']}: Invalid data - {error_msg}")
                     continue

                member_id = str(ObjectId())
                qr_result = qr_utils.generate_member_qr_code(member_id, name)
                
                new_member = MemberModel.create(data, qr_result['qr_data'])
                new_member['_id'] = ObjectId(member_id)
                
                db.members.insert_one(new_member)
                results["inserted"] += 1
                
            except Exception as e:
                results["errors"].append(f"Row {results['total']}: Database error - {str(e)}")
                logger.error(f"Import error row {results['total']}: {str(e)}")

        logger.info(f"Batch import completed. Total: {results['total']}, Inserted: {results['inserted']}")
        return jsonify(results)

    except Exception as e:
        logger.error(f"Error importing members: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500
