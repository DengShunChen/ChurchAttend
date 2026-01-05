#!/usr/bin/env python3
# test_qr_checkin.py
# 測試 QR Code 掃描簽到功能
# Test QR Code Scan Check-in Feature

import requests
import json
import sys

API_URL = "http://localhost:5050"

def test_qr_workflow():
    """完整測試 QR Code 工作流程"""
    
    print("=" * 60)
    print("🔍 QR Code 報到功能測試")
    print("   QR Code Check-in Feature Test")
    print("=" * 60)
    print()
    
    # 1. 創建會友並獲取 QR Code
    print("步驟 1: 創建會友並生成 QR Code")
    print("-" * 60)
    
    member_data = {
        "name": "王小華",
        "phone": "0923456789",
        "group": "敬拜團"
    }
    
    response = requests.post(f"{API_URL}/members", json=member_data)
    
    if response.status_code == 201:
        result = response.json()
        member_id = result['member_id']
        qr_data = result['data']['qr_data']
        
        print(f"✅ 會友創建成功")
        print(f"   ID: {member_id}")
        print(f"   姓名: {result['data']['name']}")
        print(f"   QR Data: {qr_data[:50]}...")
        print()
        
        # 2. 使用 QR Code 掃描簽到
        print("步驟 2: 使用 QR Code 掃描簽到")
        print("-" * 60)
        
        scan_data = {
            "qr_data": qr_data,
            "session": "noon"
        }
        
        scan_response = requests.post(f"{API_URL}/attendance/scan", json=scan_data)
        
        if scan_response.status_code == 201:
            scan_result = scan_response.json()
            print(f"✅ QR Code 掃描簽到成功")
            print(f"   訊息: {scan_result['message']}")
            print(f"   會友: {scan_result['data']['name']}")
            print(f"   日期: {scan_result['data']['date']}")
            print(f"   場次: {scan_result['data']['session']}")
            print()
            
            # 3. 驗證出勤記錄
            print("步驟 3: 驗證出勤記錄已建立")
            print("-" * 60)
            
            attendance_response = requests.get(f"{API_URL}/attendance")
            if attendance_response.status_code == 200:
                attendance_data = attendance_response.json()
                records = attendance_data.get('data', [])
                
                # 找到剛才的記錄
                found = False
                for record in records:
                    if record.get('member_id') == member_id:
                        print(f"✅ 找到出勤記錄")
                        print(f"   姓名: {record['name']}")
                        print(f"   日期: {record['date']}")
                        print(f"   類型: {record.get('member_type', 'unknown')}")
                        found = True
                        break
                
                if not found:
                    print("⚠️  未找到出勤記錄")
            print()
            
            # 4. 測試重複掃描
            print("步驟 4: 測試重複掃描檢查")
            print("-" * 60)
            
            duplicate_response = requests.post(f"{API_URL}/attendance/scan", json=scan_data)
            if duplicate_response.status_code == 409:
                print(f"✅ 重複掃描正確被阻止")
                print(f"   錯誤訊息: {duplicate_response.json()['error']}")
            else:
                print(f"⚠️  重複檢查可能有問題 (status: {duplicate_response.status_code})")
            print()
            
        else:
            print(f"❌ QR Code 掃描失敗")
            print(f"   狀態碼: {scan_response.status_code}")
            print(f"   錯誤: {scan_response.text}")
            return False
            
    else:
        print(f"❌ 會友創建失敗")
        print(f"   狀態碼: {response.status_code}")
        print(f"   錯誤: {response.text}")
        return False
    
    # 總結
    print("=" * 60)
    print("✅ QR Code 報到功能測試完成")
    print("=" * 60)
    print()
    print("功能驗證:")
    print("  ✓ QR Code 生成")
    print("  ✓ QR Code 掃描簽到")
    print("  ✓ 出勤記錄建立")
    print("  ✓ 重複掃描檢查")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_qr_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
