#!/usr/bin/env python3
# test_standalone.py
# 測試不需要資料庫的功能
# Test standalone functionality without database

import sys
from datetime import datetime

def test_config():
    """測試配置模組"""
    print("=" * 60)
    print("測試配置模組 / Testing Config Module")
    print("=" * 60)
    try:
        from config import get_config
        config = get_config('development')
        print(f"✓ 配置載入成功")
        print(f"  - MongoDB Host: {config.MONGODB_HOST}")
        print(f"  - MongoDB DB: {config.MONGODB_DB}")
        print(f"  - Flask Port: {config.PORT}")
        print(f"  - QR Secret Key: {'*' * 20} (hidden)")
        return True
    except Exception as e:
        print(f"✗ 配置載入失敗: {e}")
        return False

def test_models():
    """測試資料模型"""
    print("\n" + "=" * 60)
    print("測試資料模型 / Testing Data Models")
    print("=" * 60)
    
    from models import AttendanceModel, MemberModel, VisitorModel, SessionModel
    
    # 測試出勤驗證
    print("\n1. 出勤資料驗證:")
    
    # 有效資料
    valid_data = {'date': '2025-12-30', 'name': '王小明'}
    is_valid, error = AttendanceModel.validate(valid_data)
    print(f"  有效資料: {is_valid} {'✓' if is_valid else '✗'}")
    
    # 無效資料 - 缺少姓名
    invalid_data = {'date': '2025-12-30'}
    is_valid, error = AttendanceModel.validate(invalid_data)
    print(f"  缺少姓名: {not is_valid} {'✓' if not is_valid else '✗'}")
    print(f"    錯誤訊息: {error}")
    
    # 無效資料 - 錯誤日期格式
    invalid_data = {'date': '2025/12/30', 'name': '王小明'}
    is_valid, error = AttendanceModel.validate(invalid_data)
    print(f"  錯誤日期: {not is_valid} {'✓' if not is_valid else '✗'}")
    print(f"    錯誤訊息: {error}")
    
    # 測試會友驗證
    print("\n2. 會友資料驗證:")
    valid_member = {'name': '李小華', 'phone': '0912345678'}
    is_valid, error = MemberModel.validate(valid_member)
    print(f"  有效會友: {is_valid} {'✓' if is_valid else '✗'}")
    
    invalid_phone = {'name': '李小華', 'phone': '123'}
    is_valid, error = MemberModel.validate(invalid_phone)
    print(f"  無效電話: {not is_valid} {'✓' if not is_valid else '✗'}")
    print(f"    錯誤訊息: {error}")
    
    # 測試場次模型
    print("\n3. 場次管理:")
    sessions = SessionModel.get_all()
    print(f"  場次數量: {len(sessions)} {'✓' if len(sessions) == 3 else '✗'}")
    for session in sessions:
        print(f"    - {session['name']} ({session['time']})")
    
    print(f"  驗證場次 ID: {SessionModel.is_valid('noon')} {'✓' if SessionModel.is_valid('noon') else '✗'}")
    print(f"  無效場次 ID: {not SessionModel.is_valid('invalid')} {'✓' if not SessionModel.is_valid('invalid') else '✗'}")
    
    return True

def test_qr_utils():
    """測試 QR Code 工具"""
    print("\n" + "=" * 60)
    print("測試 QR Code 工具 / Testing QR Utils")
    print("=" * 60)
    
    try:
        import qr_utils
        
        # 測試 QR Code 生成
        print("\n1. QR Code 生成:")
        member_id = "test123"
        member_name = "測試會友"
        
        qr_result = qr_utils.generate_member_qr_code(member_id, member_name)
        print(f"  生成成功: ✓")
        print(f"  QR 資料長度: {len(qr_result['qr_data'])} bytes")
        print(f"  QR 圖片: {qr_result['qr_image'][:50]}... (base64)")
        
        # 測試 QR Code 驗證
        print("\n2. QR Code 驗證:")
        is_valid, member_data = qr_utils.validate_qr_scan(qr_result['qr_data'])
        print(f"  驗證成功: {is_valid} {'✓' if is_valid else '✗'}")
        if is_valid:
            print(f"  解密 ID: {member_data['id']} {'✓' if member_data['id'] == member_id else '✗'}")
            print(f"  解密姓名: {member_data['name']} {'✓' if member_data['name'] == member_name else '✗'}")
        
        # 測試無效 QR Code
        print("\n3. 無效 QR Code:")
        is_valid, _ = qr_utils.validate_qr_scan("invalid_qr_data")
        print(f"  正確拒絕: {not is_valid} {'✓' if not is_valid else '✗'}")
        
        return True
        
    except Exception as e:
        print(f"✗ QR Code 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validators():
    """測試驗證工具"""
    print("\n" + "=" * 60)
    print("測試驗證工具 / Testing Validators")
    print("=" * 60)
    
    from utils.validators import (
        validate_object_id, validate_date, validate_phone, 
        validate_pagination, sanitize_string
    )
    
    # 測試 ObjectId 驗證
    print("\n1. ObjectId 驗證:")
    valid_id = "507f1f77bcf86cd799439011"
    is_valid, _ = validate_object_id(valid_id)
    print(f"  有效 ID: {is_valid} {'✓' if is_valid else '✗'}")
    
    invalid_id = "invalid"
    is_valid, error = validate_object_id(invalid_id)
    print(f"  無效 ID: {not is_valid} {'✓' if not is_valid else '✗'}")
    
    # 測試日期驗證
    print("\n2. 日期驗證:")
    is_valid, _ = validate_date("2025-12-30")
    print(f"  有效日期: {is_valid} {'✓' if is_valid else '✗'}")
    
    is_valid, error = validate_date("2025/12/30")
    print(f"  錯誤格式: {not is_valid} {'✓' if not is_valid else '✗'}")
    
    # 測試電話驗證
    print("\n3. 電話驗證:")
    is_valid, _ = validate_phone("0912345678")
    print(f"  有效電話: {is_valid} {'✓' if is_valid else '✗'}")
    
    is_valid, _ = validate_phone("")
    print(f"  空電話(允許): {is_valid} {'✓' if is_valid else '✗'}")
    
    is_valid, error = validate_phone("123")
    print(f"  無效電話: {not is_valid} {'✓' if not is_valid else '✗'}")
    
    # 測試分頁驗證
    print("\n4. 分頁驗證:")
    is_valid, error, page, page_size = validate_pagination(1, 50)
    print(f"  有效分頁: {is_valid} {'✓' if is_valid else '✗'} (page={page}, size={page_size})")
    
    is_valid, error, _, _ = validate_pagination(-1, 50)
    print(f"  負數頁碼: {not is_valid} {'✓' if not is_valid else '✗'}")
    
    # 測試字串清理
    print("\n5. 字串清理:")
    clean = sanitize_string("  test  ")
    print(f"  移除空白: '{clean}' {'✓' if clean == 'test' else '✗'}")
    
    clean = sanitize_string("test\x00control")
    print(f"  移除控制字元: '{clean}' {'✓' if clean == 'testcontrol' else '✗'}")
    
    return True

def main():
    """主測試函數"""
    print("\n")
    print("🧪 " + "=" * 58)
    print("   高榮禮拜堂出勤系統 - 獨立功能測試")
    print("   Church Attendance System - Standalone Tests")
    print("=" * 62)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 執行所有測試
    results.append(("配置模組", test_config()))
    results.append(("資料模型", test_models()))
    results.append(("QR Code", test_qr_utils()))
    results.append(("驗證工具", test_validators()))
    
    # 總結
    print("\n" + "=" * 62)
    print("測試總結 / Test Summary")
    print("=" * 62)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 62)
    print(f"總計: {passed}/{total} 通過")
    print(f"Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 所有測試通過！")
        print("   All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 個測試失敗")
        print(f"   {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
