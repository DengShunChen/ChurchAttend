#!/usr/bin/env python3
# test_imports.py
# 測試所有模組導入
# Test all module imports

import sys

def test_imports():
    """測試所有模組是否能正常導入"""
    modules_to_test = [
        'config',
        'database',
        'models',
        'qr_utils',
        'utils.logger',
        'utils.validators',
        'routes.attendance',
        'routes.members',
        'routes.visitors',
        'routes.stats',
        'routes.sessions',
        'routes.health',
        'app'
    ]
    
    failed = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append((module, str(e)))
    
    print("\n" + "=" * 50)
    if not failed:
        print("所有模組導入成功！")
        print("All modules imported successfully!")
        return 0
    else:
        print(f"失敗: {len(failed)} 個模組")
        print(f"Failed: {len(failed)} modules")
        for module, error in failed:
            print(f"  - {module}: {error}")
        return 1

if __name__ == '__main__':
    sys.exit(test_imports())
