# models.py
# 資料模型定義
# Data Models Definition

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
import re


class BaseModel:
    """基礎模型類"""
    
    @staticmethod
    def to_json(obj: Any) -> Any:
        """
        轉換 MongoDB 對象為 JSON 可序列化格式
        Convert MongoDB object to JSON serializable format
        """
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: BaseModel.to_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [BaseModel.to_json(item) for item in obj]
        return obj


class AttendanceModel(BaseModel):
    """出勤記錄模型"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        驗證出勤資料
        Validate attendance data
        
        Returns:
            (is_valid, error_message)
        """
        if not data:
            return False, "請求資料不能為空 / Request data cannot be empty"
        
        # 驗證必填欄位
        if 'date' not in data or not data['date']:
            return False, "日期欄位為必填 / Date field is required"
        
        if 'name' not in data or not data['name']:
            return False, "姓名欄位為必填 / Name field is required"
        
        # 驗證姓名長度
        name = data['name'].strip()
        if len(name) < 1 or len(name) > 50:
            return False, "姓名長度必須在 1-50 個字元之間 / Name length must be between 1-50 characters"
        
        # 驗證日期格式
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return False, "日期格式錯誤，請使用 YYYY-MM-DD 格式 / Invalid date format, please use YYYY-MM-DD"
        
        # 驗證場次（如果提供）
        if 'session' in data and data['session']:
            valid_sessions = ['morning', 'noon', 'evening']
            if data['session'] not in valid_sessions:
                return False, f"無效的場次 / Invalid session. Must be one of: {', '.join(valid_sessions)}"
        
        return True, None
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        建立出勤記錄
        Create attendance record
        """
        return {
            'date': data['date'],
            'name': data['name'].strip(),
            'member_type': data.get('member_type', 'visitor'),
            'member_id': data.get('member_id'),
            'session': data.get('session', 'noon'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def to_dict(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換為字典格式
        Convert to dictionary format
        """
        return {
            '_id': str(record['_id']),
            'date': record['date'],
            'name': record['name'],
            'member_type': record.get('member_type', 'visitor'),
            'member_id': record.get('member_id'),
            'session': record.get('session'),
            'created_at': record.get('created_at'),
            'updated_at': record.get('updated_at')
        }


class MemberModel(BaseModel):
    """會友模型"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        驗證會友資料
        Validate member data
        """
        if not data.get('name'):
            return False, "姓名為必填 / Name is required"
        
        name = data['name'].strip()
        if len(name) < 1 or len(name) > 50:
            return False, "姓名長度必須在 1-50 個字元之間 / Name length must be between 1-50 characters"
        
        # 驗證電話號碼格式（如果提供）
        if data.get('phone'):
            phone = data['phone'].strip()
            # 台灣手機號碼格式：09xx-xxxxxx 或 09xxxxxxxx
            if not re.match(r'^09\d{8}$|^09\d{2}-?\d{6}$', phone.replace('-', '')):
                return False, "電話號碼格式錯誤 / Invalid phone number format"
        
        return True, None
    
    @staticmethod
    def create(data: Dict[str, Any], qr_data: str) -> Dict[str, Any]:
        """
        建立會友記錄
        Create member record
        """
        return {
            'name': data['name'].strip(),
            'phone': data.get('phone', '').strip(),
            'group': data.get('group', '').strip(),
            'group': data.get('group', '').strip(),
            'birthday': data.get('birthday', ''),
            'address': data.get('address', ''),
            'email': data.get('email', ''),
            'line_id': data.get('line_id', ''),
            'shepherding_notes': [],
            'last_attended_date': None,
            'qr_data': qr_data,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def to_dict(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換為字典格式
        Convert to dictionary format
        """
        return {
            '_id': str(record['_id']),
            'name': record['name'],
            'phone': record.get('phone', ''),
            'group': record.get('group', ''),
            'birthday': record.get('birthday', ''),
            'address': record.get('address', ''),
            'email': record.get('email', ''),
            'line_id': record.get('line_id', ''),
            'shepherding_notes': record.get('shepherding_notes', []),
            'last_attended_date': record.get('last_attended_date'),
            'qr_data': record.get('qr_data', ''),
            'created_at': record.get('created_at'),
            'updated_at': record.get('updated_at')
        }


class VisitorModel(BaseModel):
    """訪客模型"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        驗證訪客資料
        Validate visitor data
        """
        if not data.get('name'):
            return False, "姓名為必填 / Name is required"
        
        name = data['name'].strip()
        if len(name) < 1 or len(name) > 50:
            return False, "姓名長度必須在 1-50 個字元之間 / Name length must be between 1-50 characters"
        
        # 驗證電話號碼（如果提供）
        if data.get('phone'):
            phone = data['phone'].strip()
            if not re.match(r'^09\d{8}$|^09\d{2}-?\d{6}$', phone.replace('-', '')):
                return False, "電話號碼格式錯誤 / Invalid phone number format"
        
        return True, None
    
    @staticmethod
    def create(data: Dict[str, Any], first_visit_date: str) -> Dict[str, Any]:
        """
        建立訪客記錄
        Create visitor record
        """
        return {
            'name': data['name'].strip(),
            'phone': data.get('phone', '').strip(),
            'how_to_know': data.get('how_to_know', '').strip(),
            'first_visit_date': first_visit_date,
            'last_visit_date': first_visit_date,
            'visit_count': 1,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def to_dict(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換為字典格式
        Convert to dictionary format
        """
        return {
            '_id': str(record['_id']),
            'name': record['name'],
            'phone': record.get('phone', ''),
            'how_to_know': record.get('how_to_know', ''),
            'first_visit_date': record['first_visit_date'],
            'last_visit_date': record.get('last_visit_date'),
            'visit_count': record.get('visit_count', 1),
            'created_at': record.get('created_at'),
            'updated_at': record.get('updated_at')
        }


class SessionModel(BaseModel):
    """場次模型"""
    
    SESSIONS = [
        {'id': 'morning', 'name': '早堂', 'time': '09:00'},
        {'id': 'noon', 'name': '午堂', 'time': '11:00'},
        {'id': 'evening', 'name': '晚堂', 'time': '19:00'}
    ]
    
    @classmethod
    def get_all(cls) -> List[Dict[str, str]]:
        """取得所有場次"""
        return cls.SESSIONS
    
    @classmethod
    def get_by_id(cls, session_id: str) -> Optional[Dict[str, str]]:
        """根據 ID 取得場次"""
        return next((s for s in cls.SESSIONS if s['id'] == session_id), None)
    
    @classmethod
    def is_valid(cls, session_id: str) -> bool:
        """驗證場次 ID"""
        return any(s['id'] == session_id for s in cls.SESSIONS)
