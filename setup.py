#!/usr/bin/env python3
# setup.py
# 系統初始化腳本
# System Setup Script

import os
import sys
import subprocess

def check_requirements():
    """檢查系統需求"""
    print("🔍 檢查系統需求...")
    
    # 檢查 Python 版本
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 或更高版本是必需的")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # 檢查 Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✓ Docker 已安裝")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker 未安裝或無法訪問")
        return False
    
    return True

def install_dependencies():
    """安裝 Python 依賴"""
    print("\n📦 安裝 Python 依賴...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ 依賴安裝完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依賴安裝失敗")
        return False

def check_env_file():
    """檢查 .env 檔案"""
    print("\n📝 檢查環境配置...")
    
    if not os.path.exists('.env'):
        print("⚠️  .env 檔案不存在")
        print("正在從 .env.example 創建...")
        
        try:
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✓ .env 檔案已創建")
            print("⚠️  請檢查並更新 .env 中的配置，特別是 QR_SECRET_KEY")
            return False  # 需要用戶手動配置
        except Exception as e:
            print(f"❌ 創建 .env 失敗: {e}")
            return False
    
    # 檢查關鍵配置
    with open('.env', 'r') as f:
        content = f.read()
        
    if 'QR_SECRET_KEY=your-fernet-key' in content or 'QR_SECRET_KEY=' not in content:
        print("⚠️  QR_SECRET_KEY 未配置")
        print("執行以下命令生成密鑰:")
        print("  python3 scripts/generate_qr_key.py")
        return False
    
    print("✓ 環境配置檔案存在")
    return True

def main():
    """主函數"""
    print("=" * 60)
    print("🏛️  高榮禮拜堂主日崇拜報到系統 - 初始化")
    print("   Church Attendance System - Setup")
    print("=" * 60)
    
    # 檢查需求
    if not check_requirements():
        print("\n❌ 系統需求檢查失敗")
        return 1
    
    # 安裝依賴
    if not install_dependencies():
        print("\n❌ 依賴安裝失敗")
        return 1
    
    # 檢查環境配置
    env_ready = check_env_file()
    
    print("\n" + "=" * 60)
    print("✅ 初始化完成！")
    print("=" * 60)
    
    if not env_ready:
        print("\n⚠️  下一步:")
        print("1. 生成 QR Code 密鑰:")
        print("   python3 scripts/generate_qr_key.py")
        print("2. 更新 .env 檔案中的 QR_SECRET_KEY")
        print("3. 啟動系統:")
        print("   使用 Docker: ./build.sh")
        print("   使用 Docker Compose: ./build_compose.sh")
        print("   開發模式: python3 app.py")
    else:
        print("\n🚀 可以啟動系統了:")
        print("   使用 Docker: ./build.sh")
        print("   使用 Docker Compose: ./build_compose.sh")
        print("   開發模式: python3 app.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
