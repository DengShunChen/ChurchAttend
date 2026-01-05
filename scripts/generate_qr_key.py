# scripts/generate_qr_key.py
# 生成 QR Code 加密密鑰
# Generate QR Code Encryption Key

from cryptography.fernet import Fernet

def generate_key():
    """生成 Fernet 密鑰"""
    key = Fernet.generate_key()
    print("=" * 50)
    print("QR Code 加密密鑰已生成:")
    print("Generated QR Code Encryption Key:")
    print("=" * 50)
    print(key.decode())
    print("=" * 50)
    print("\n請將此密鑰添加到 .env 檔案:")
    print("Please add this key to your .env file:")
    print(f"QR_SECRET_KEY={key.decode()}")
    print("\n警告：請妥善保管此密鑰，遺失將無法解密現有 QR Code！")
    print("WARNING: Keep this key safe! Losing it will make existing QR codes unreadable!")
    print("=" * 50)

if __name__ == '__main__':
    generate_key()
