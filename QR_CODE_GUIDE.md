# QR Code 報到功能使用說明
# QR Code Check-in Feature Guide

## 📱 功能概述

QR Code 報到功能讓會友可以使用專屬的 QR Code 快速完成簽到，無需手動輸入資料。

### 優點
- ⚡ **快速** - 掃描 QR Code 即可完成簽到
- 🔒 **安全** - QR Code 資料經過加密，防止偽造
- ✅ **準確** - 自動識別會友身份，避免輸入錯誤
- 📊 **追蹤** - 系統自動記錄出勤，便於統計

---

## 🔧 系統架構

### 加密機制
- 使用 **Fernet 加密** (對稱加密)
- 密鑰固定儲存在環境變數 `QR_SECRET_KEY`
- 確保 QR Code 在系統重啟後仍然有效

### QR Code 內容
加密後的 QR Code 包含：
- 會友 ID (MongoDB ObjectId)
- 會友姓名
- 時間戳記（生成時間）

---

## 👤 管理員操作指南

### 1. 為會友建立 QR Code

#### 方式一：使用 API

**端點**: `POST /members`

**請求範例**:
```bash
curl -X POST http://localhost:5050/members \
  -H "Content-Type: application/json" \
  -d '{
    "name": "王小明",
    "phone": "0912345678",
    "group": "青年團契"
  }'
```

**回應範例**:
```json
{
  "message": "會友新增成功 / Member added successfully",
  "member_id": "6953446d4212d35148da19d0",
  "qr_image": "data:image/png;base64,iVBORw0KGgo...",
  "data": {
    "name": "王小明",
    "phone": "0912345678",
    "group": "青年團契",
    "qr_data": "Z0FBQUFBQnBVMFJ0..."
  }
}
```

#### 方式二：使用 Python 腳本

```python
import requests

# 建立會友
response = requests.post('http://localhost:5050/members', json={
    "name": "王小明",
    "phone": "0912345678",
    "group": "青年團契"
})

result = response.json()

# 取得 QR Code
qr_image = result['qr_image']  # Base64 格式
qr_data = result['data']['qr_data']  # 加密資料

# 儲存 QR Code 圖片
import base64
image_data = base64.b64decode(qr_image.split(',')[1])
with open(f'{result["data"]["name"]}_qr.png', 'wb') as f:
    f.write(image_data)
```

### 2. 重新取得會友的 QR Code

如果 QR Code 遺失，可以重新取得：

**端點**: `GET /members/{member_id}/qrcode`

**請求範例**:
```bash
curl http://localhost:5050/members/6953446d4212d35148da19d0/qrcode
```

**回應**:
```json
{
  "member_id": "6953446d4212d35148da19d0",
  "name": "王小明",
  "qr_image": "data:image/png;base64,...",
  "qr_data": "Z0FBQUFBQnBVMFJ0..."
}
```

### 3. 列印或分發 QR Code

1. **下載 QR Code 圖片**
   - 從 API 回應中取得 `qr_image` (Base64)
   - 轉換為圖片檔案 (PNG)

2. **列印選項**
   - 📄 單張會友卡 (含姓名、QR Code)
   - 📋 批次列印多位會友
   - 📱 傳送到會友手機 (電子版)

3. **建議格式**
   ```
   ┌─────────────────────┐
   │  高榮禮拜堂主日崇拜  │
   │                     │
   │   王小明            │
   │   青年團契          │
   │                     │
   │   [QR CODE IMAGE]   │
   │                     │
   │  請於報到時掃描此碼  │
   └─────────────────────┘
   ```

---

## 📱 會友使用指南

### 方式一：管理員掃描

1. 會友出示 QR Code (紙本或手機)
2. 管理員使用掃描器或手機相機掃描
3. 將掃描結果（加密字串）傳送到系統
4. 系統自動完成簽到

### 方式二：自助掃描 (未來功能)

1. 會友使用手機開啟前端掃描頁面
2. 允許相機權限
3. 對準其他會友的 QR Code 或自己的 QR Code
4. 系統自動識別並完成簽到

---

## 🔌 API 使用說明

### 掃描 QR Code 簽到

**端點**: `POST /attendance/scan`

**請求格式**:
```json
{
  "qr_data": "Z0FBQUFBQnBVMFJ0...",
  "session": "noon"
}
```

**參數說明**:
- `qr_data` (必填): 從 QR Code 掃描得到的加密字串
- `session` (選填): 場次 ID，預設為 `noon`
  - `morning`: 早堂 (09:00)
  - `noon`: 午堂 (11:00)
  - `evening`: 晚堂 (19:00)

**成功回應** (201):
```json
{
  "message": "王小明 簽到成功！ / Check-in successful!",
  "name": "王小明",
  "timestamp": "2025-12-30T03:18:05.975132"
}
```

**錯誤回應**:

1. **QR Code 無效** (400):
```json
{
  "error": "QR Code 無效或已過期 / Invalid or expired QR code"
}
```

2. **重複簽到** (409):
```json
{
  "error": "王小明 已經在 2025-12-30 報到過了"
}
```

3. **會友不存在** (404):
```json
{
  "error": "找不到對應的會友記錄 / Member not found"
}
```

---

## 💻 程式碼範例

### Python 範例

```python
import requests

def scan_qr_checkin(qr_data, session='noon'):
    """掃描 QR Code 並完成簽到"""
    url = 'http://localhost:5050/attendance/scan'
    
    response = requests.post(url, json={
        'qr_data': qr_data,
        'session': session
    })
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ {result['name']} 簽到成功！")
        return True
    elif response.status_code == 409:
        print("⚠️ 已經簽到過了")
        return False
    else:
        print(f"❌ 簽到失敗: {response.json()['error']}")
        return False

# 使用範例
qr_data = "Z0FBQUFBQnBVMFJ0..."
scan_qr_checkin(qr_data, session='noon')
```

### JavaScript 範例 (前端)

```javascript
async function scanQRCode(qrData) {
    try {
        const response = await fetch('http://localhost:5050/attendance/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                qr_data: qrData,
                session: 'noon'
            })
        });
        
        const result = await response.json();
        
        if (response.status === 201) {
            alert(`✅ ${result.name} 簽到成功！`);
            return true;
        } else if (response.status === 409) {
            alert('⚠️ 已經簽到過了');
            return false;
        } else {
            alert(`❌ ${result.error}`);
            return false;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ 簽到失敗');
        return false;
    }
}
```

### 批次處理範例

```python
import requests

def batch_generate_qr_codes(members):
    """批次生成會友 QR Code"""
    results = []
    
    for member in members:
        response = requests.post('http://localhost:5050/members', json=member)
        
        if response.status_code == 201:
            result = response.json()
            results.append({
                'name': result['data']['name'],
                'qr_image': result['qr_image'],
                'qr_data': result['data']['qr_data']
            })
            print(f"✅ {result['data']['name']} QR Code 生成成功")
        else:
            print(f"❌ {member['name']} 生成失敗")
    
    return results

# 使用範例
members = [
    {"name": "王小明", "phone": "0912345678", "group": "青年團契"},
    {"name": "李小華", "phone": "0923456789", "group": "敬拜團"},
    {"name": "陳大明", "phone": "0934567890", "group": "服事組"}
]

qr_codes = batch_generate_qr_codes(members)
```

---

## ⚠️ 重要注意事項

### 安全性

1. **保護 QR_SECRET_KEY**
   - 此密鑰儲存在 `.env` 檔案
   - **絕對不要** 提交到版本控制系統
   - **務必** 在生產環境中更改預設密鑰

2. **QR Code 唯一性**
   - 每個會友有唯一的 QR Code
   - QR Code 包含加密的會友資訊
   - 無法通過反向工程取得明文

3. **防止重複掃描**
   - 系統自動檢查當日是否已簽到
   - 同一天同一場次只能簽到一次

### 最佳實踐

1. **定期備份**
   - 定期備份 `.env` 檔案（含 QR_SECRET_KEY）
   - 如果密鑰遺失，所有 QR Code 將失效

2. **QR Code 管理**
   - 建議為每位會友列印紙本 QR Code
   - 同時提供電子版（手機）選項
   - 遺失時可重新取得（密鑰不變）

3. **錯誤處理**
   - 掃描失敗時顯示明確錯誤訊息
   - 提供手動簽到備用方案
   - 記錄異常掃描嘗試

### 故障排除

**問題 1: QR Code 掃描失敗**
- 檢查 QR Code 是否清晰可讀
- 確認系統時間正確
- 驗證 `QR_SECRET_KEY` 是否正確設定

**問題 2: 重複簽到錯誤**
- 確認是否真的已經簽到
- 檢查日期和場次設定
- 查看出勤記錄確認

**問題 3: 會友不存在錯誤**
- 確認會友資料已建立
- 檢查 MongoDB 資料庫連接
- 驗證 member_id 是否正確

---

## 🔄 工作流程圖

```
管理員操作:
┌─────────────┐
│ 建立會友資料  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 系統生成 QR  │
│   (加密)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 列印/分發 QR │
└─────────────┘

會友使用:
┌─────────────┐
│ 出示 QR Code │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 掃描 QR Code │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 系統解密驗證  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 檢查重複簽到  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 建立出勤記錄  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 簽到成功 ✓   │
└─────────────┘
```

---

## 📞 技術支援

### API 端點總覽

| 端點 | 方法 | 說明 |
|-----|------|-----|
| `/members` | POST | 建立會友並生成 QR Code |
| `/members/{id}/qrcode` | GET | 取得會友 QR Code |
| `/attendance/scan` | POST | QR Code 掃描簽到 |
| `/attendance` | GET | 查詢出勤記錄 |

### 相關文件

- [API 完整文件](README.md)
- [系統架構說明](OPTIMIZATION_SUMMARY.md)
- [測試報告](COMPLETE_TEST_REPORT.md)

### 測試工具

使用提供的測試腳本：
```bash
# 測試 QR Code 完整流程
python3 test_qr_checkin.py

# 測試所有 API
./api_test.sh
```

---

## 📝 版本記錄

### v2.0.0 (2025-12-30)
- ✅ 實作 QR Code 生成功能
- ✅ 實作 QR Code 掃描簽到
- ✅ 加入 Fernet 加密機制
- ✅ 支援固定密鑰（環境變數）
- ✅ 重複簽到檢查
- ✅ 完整的 API 端點

---

**最後更新**: 2025-12-30  
**文件版本**: 1.0  
**系統版本**: 2.0.0
