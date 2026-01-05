# utils/logger.py
# 日誌工具
# Logging Utility

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON 格式日誌格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日誌為 JSON
        Format log as JSON
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加異常資訊
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # 添加額外字段
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name: str, level: str = 'INFO', use_json: bool = False) -> logging.Logger:
    """
    設定日誌記錄器
    Setup logger
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌等級
        use_json: 是否使用 JSON 格式
    
    Returns:
        Logger 對象
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 建立 console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # 設定格式
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def log_request(logger: logging.Logger, method: str, path: str, 
                status_code: int, duration_ms: float, **kwargs):
    """
    記錄 HTTP 請求
    Log HTTP request
    """
    extra_data = {
        'request_method': method,
        'request_path': path,
        'status_code': status_code,
        'duration_ms': duration_ms,
        **kwargs
    }
    
    message = f"{method} {path} {status_code} {duration_ms:.2f}ms"
    
    # 根據狀態碼選擇日誌等級
    if status_code >= 500:
        logger.error(message, extra={'extra_data': extra_data})
    elif status_code >= 400:
        logger.warning(message, extra={'extra_data': extra_data})
    else:
        logger.info(message, extra={'extra_data': extra_data})


def log_db_operation(logger: logging.Logger, operation: str, 
                     collection: str, duration_ms: float, **kwargs):
    """
    記錄資料庫操作
    Log database operation
    """
    extra_data = {
        'db_operation': operation,
        'collection': collection,
        'duration_ms': duration_ms,
        **kwargs
    }
    
    message = f"DB {operation} on {collection} took {duration_ms:.2f}ms"
    logger.debug(message, extra={'extra_data': extra_data})
