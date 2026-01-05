# utils/validators.py
# 輸入驗證工具
# Input Validation Utilities

from functools import wraps
from flask import request, jsonify
from typing import Callable, Any, Dict, List, Optional
import re


def validate_json(func: Callable) -> Callable:
    """
    驗證請求包含 JSON 資料的裝飾器
    Decorator to validate request contains JSON data
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'error': '請求必須包含 JSON 資料 / Request must contain JSON data'
            }), 400
        return func(*args, **kwargs)
    return wrapper


def validate_fields(required_fields: List[str], optional_fields: Optional[List[str]] = None):
    """
    驗證請求欄位的裝飾器
    Decorator to validate request fields
    
    Args:
        required_fields: 必填欄位列表
        optional_fields: 選填欄位列表
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.json
            
            if not data:
                return jsonify({
                    'error': '請求資料不能為空 / Request data cannot be empty'
                }), 400
            
            # 檢查必填欄位
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return jsonify({
                    'error': f'缺少必填欄位 / Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            # 檢查未知欄位
            all_fields = set(required_fields + (optional_fields or []))
            unknown_fields = [field for field in data.keys() if field not in all_fields]
            if unknown_fields:
                return jsonify({
                    'error': f'未知欄位 / Unknown fields: {", ".join(unknown_fields)}'
                }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_object_id(object_id: str) -> tuple[bool, Optional[str]]:
    """
    驗證 MongoDB ObjectId 格式
    Validate MongoDB ObjectId format
    
    Returns:
        (is_valid, error_message)
    """
    if not object_id:
        return False, "物件 ID 不能為空 / Object ID cannot be empty"
    
    if not re.match(r'^[0-9a-fA-F]{24}$', object_id):
        return False, "無效的物件 ID 格式 / Invalid object ID format"
    
    return True, None


def validate_date(date_str: str) -> tuple[bool, Optional[str]]:
    """
    驗證日期格式 (YYYY-MM-DD)
    Validate date format
    
    Returns:
        (is_valid, error_message)
    """
    if not date_str:
        return False, "日期不能為空 / Date cannot be empty"
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, "日期格式錯誤，請使用 YYYY-MM-DD 格式 / Invalid date format, use YYYY-MM-DD"
    
    # 驗證日期是否合法
    from datetime import datetime
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "無效的日期 / Invalid date"


def validate_phone(phone: str) -> tuple[bool, Optional[str]]:
    """
    驗證台灣手機號碼格式
    Validate Taiwan phone number format
    
    Returns:
        (is_valid, error_message)
    """
    if not phone:
        return True, None  # 電話號碼為選填
    
    # 移除空格和連字符
    phone = phone.replace(' ', '').replace('-', '')
    
    # 台灣手機號碼：09xxxxxxxx
    if not re.match(r'^09\d{8}$', phone):
        return False, "電話號碼格式錯誤 / Invalid phone number format (should be 09xxxxxxxx)"
    
    return True, None


def validate_pagination(page: Any, page_size: Any, max_page_size: int = 500) -> tuple[bool, Optional[str], int, int]:
    """
    驗證分頁參數
    Validate pagination parameters
    
    Returns:
        (is_valid, error_message, page, page_size)
    """
    try:
        page = int(page) if page else 1
        page_size = int(page_size) if page_size else 50
    except (ValueError, TypeError):
        return False, "分頁參數必須為整數 / Pagination parameters must be integers", 0, 0
    
    if page < 1:
        return False, "頁碼必須大於 0 / Page number must be greater than 0", 0, 0
    
    if page_size < 1:
        return False, "每頁數量必須大於 0 / Page size must be greater than 0", 0, 0
    
    if page_size > max_page_size:
        return False, f"每頁數量不能超過 {max_page_size} / Page size cannot exceed {max_page_size}", 0, 0
    
    return True, None, page, page_size


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    清理字串輸入
    Sanitize string input
    """
    if not value:
        return ""
    
    # 移除前後空白
    value = value.strip()
    
    # 限制長度
    if len(value) > max_length:
        value = value[:max_length]
    
    # 移除控制字元
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    return value


class ValidationError(Exception):
    """驗證錯誤異常"""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
