# qr_utils.py
# QR Code 工具函數
# QR Code Utility Functions

import qrcode
import io
import base64
from cryptography.fernet import Fernet
import os
import json

# QR Code 加密密鑰（必須從環境變數讀取固定值）
# QR Code encryption key (must be from environment variable as fixed value)
SECRET_KEY = os.getenv('QR_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("QR_SECRET_KEY environment variable is not set. Please set it in .env file.")

# 確保密鑰格式正確（Fernet 需要 32 bytes base64 編碼）
if isinstance(SECRET_KEY, str):
    SECRET_KEY = SECRET_KEY.encode()

try:
    cipher_suite = Fernet(SECRET_KEY)
except Exception as e:
    raise ValueError(f"Invalid QR_SECRET_KEY format. It must be a valid Fernet key. Error: {e}")

def generate_member_qr_data(member_id, name):
    """
    生成會友 QR Code 資料
    Generate member QR code data
    
    Args:
        member_id: 會友編號
        name: 會友姓名
    
    Returns:
        加密的 QR Code 字串
    """
    data = {
        'id': member_id,
        'name': name,
        'type': 'member'
    }
    
    # 將資料轉為 JSON 並加密
    json_data = json.dumps(data).encode()
    encrypted_data = cipher_suite.encrypt(json_data)
    
    # Base64 編碼以便儲存和傳輸
    return base64.urlsafe_b64encode(encrypted_data).decode()

def decrypt_qr_data(qr_string):
    """
    解密 QR Code 資料
    Decrypt QR code data
    
    Args:
        qr_string: 加密的 QR Code 字串
    
    Returns:
        解密後的會友資料 dict，失敗返回 None
    """
    try:
        # Base64 解碼
        encrypted_data = base64.urlsafe_b64decode(qr_string.encode())
        
        # 解密
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        
        # 解析 JSON
        data = json.loads(decrypted_data.decode())
        
        return data
    except Exception as e:
        print(f"Error decrypting QR data: {e}")
        return None

def generate_qr_image(data, size=300):
    """
    生成 QR Code 圖片
    Generate QR code image
    
    Args:
        data: 要編碼的資料
        size: 圖片尺寸（像素）
    
    Returns:
        QR Code 圖片的 base64 編碼字串
    """
    # 建立 QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # 生成圖片
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 轉換為 base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

def generate_member_qr_code(member_id, name):
    """
    為會友生成完整的 QR Code
    Generate complete QR code for a member
    
    Args:
        member_id: 會友編號
        name: 會友姓名
    
    Returns:
        包含 QR Code 圖片和資料的 dict
    """
    # 生成加密資料
    qr_data = generate_member_qr_data(member_id, name)
    
    # 生成 QR Code 圖片
    qr_image = generate_qr_image(qr_data)
    
    return {
        'qr_data': qr_data,
        'qr_image': qr_image,
        'member_id': member_id,
        'name': name
    }

def validate_qr_scan(qr_string):
    """
    驗證掃描的 QR Code
    Validate scanned QR code
    
    Args:
        qr_string: 掃描得到的 QR Code 字串
    
    Returns:
        (is_valid, member_data) tuple
    """
    member_data = decrypt_qr_data(qr_string)
    
    if member_data is None:
        return False, None
    
    # 檢查必要欄位
    if 'id' not in member_data or 'name' not in member_data:
        return False, None
    
    # 檢查類型
    if member_data.get('type') != 'member':
        return False, None
    
    return True, member_data
