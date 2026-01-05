# 高榮禮拜堂主日崇拜報到系統

<div align="center">

🏛️ **Church Attendance Management System**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-orange.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)

一個現代化、功能完善的教會出勤管理系統

</div>

---

## 📋 目錄

- [功能特色](#功能特色)
- [技術架構](#技術架構)
- [快速開始](#快速開始)
- [使用說明](#使用說明)
- [API 文件](#api-文件)
- [專案結構](#專案結構)
- [開發指南](#開發指南)
- [維護與備份](#維護與備份)

---

## ✨ 功能特色

### 核心功能
- ✅ **即時報到** - 簡單快速的報到流程
- 📊 **統計面板** - 即時顯示今日出勤、總記錄數
- 🔍 **智慧搜尋** - 依姓名即時搜尋，支援模糊比對
- 📅 **日期篩選** - 支援單日或日期範圍篩選
- 📥 **CSV 匯出** - 一鍵匯出所有出勤記錄
- 🗑️ **記錄管理** - 輕鬆刪除錯誤記錄

### 系統優化
- 🚫 **重複防護** - 自動防止同一人同一天重複報到
- ✔️ **資料驗證** - 完整的輸入欄位驗證
- 🔒 **錯誤處理** - 友善的錯誤訊息提示
- 📝 **日誌記錄** - 完整的操作日誌
- ⚡ **效能優化** - 資料庫索引提升查詢速度
- 💾 **資料持久化** - Docker Volume 確保資料安全

### 使用者體驗
- 🎨 **現代化設計** - 美觀的漸層色彩與動畫效果
- 📱 **響應式設計** - 支援手機、平板、電腦
- 🔔 **即時通知** - Toast 提示訊息
- ⌨️ **鍵盤快捷鍵** - Enter 快速提交
- 🎯 **自動聚焦** - 提升輸入效率

---

## 🏗️ 技術架構

### 後端技術
- **Web 框架**: Flask 3.0
- **WSGI 伺服器**: Gunicorn (生產環境)
- **資料庫**: MongoDB 7.0
- **其他**: Flask-CORS, pymongo

### 前端技術
- **核心**: HTML5, CSS3, JavaScript (ES6+)
- **字型**: Google Fonts (Noto Sans TC)
- **設計**: 漸層背景、卡片式布局、動畫效果

### 基礎設施
- **容器化**: Docker
- **Web 伺服器**: Nginx
- **資料持久化**: Docker Volume

---

## 🚀 快速開始

### 前置需求
- Docker (v20.10+)
- Docker Compose (可選)

### 一鍵啟動

```bash
# 1. 克隆專案
git clone <repository-url>
cd attendance

# 2. 執行建置腳本
chmod +x build.sh
./build.sh
```

### 手動啟動

```bash
# 建置映像檔
docker build -t attendance-app .

# 啟動容器
docker run -d \
    --name attendance-app \
    -p 80:80 \
    -p 5050:5050 \
    -v attendance-data:/data/db \
    --restart unless-stopped \
    attendance-app:latest
```

### 訪問系統

- 🌐 **前端介面**: http://localhost
- 🔌 **API 端點**: http://localhost:5050
- ❤️ **健康檢查**: http://localhost:5050/health

---

## 📖 使用說明

### 報到流程

1. 打開瀏覽器訪問 http://localhost
2. 系統自動填入今日日期
3. 輸入姓名
4. 點擊「確認報到」按鈕
5. 看到成功訊息，報到完成！

### 查看記錄

- **查看全部**: 右側表格顯示所有記錄
- **搜尋姓名**: 在搜尋框輸入姓名即時篩選
- **日期篩選**: 選擇開始/結束日期，點擊「篩選」

### 匯出資料

點擊「下載 CSV」按鈕，系統會下載包含所有記錄的 CSV 檔案。

### 管理記錄

如需刪除錯誤記錄，點擊該記錄旁的「刪除」按鈕即可。

---

## 🔌 API 文件

### 獲取出勤記錄
```http
GET /attendance
```

**查詢參數**:
- `date_from` (可選): 開始日期 (YYYY-MM-DD)
- `date_to` (可選): 結束日期 (YYYY-MM-DD)
- `search` (可選): 搜尋姓名

**回應範例**:
```json
[
  {
    "_id": "123456",
    "date": "2025-12-29",
    "name": "王小明"
  }
]
```

### 新增出勤記錄
```http
POST /attendance
Content-Type: application/json

{
  "date": "2025-12-29",
  "name": "王小明"
}
```

**回應範例**:
```json
{
  "message": "報到成功 / Attendance added successfully",
  "id": "123456"
}
```

### 刪除出勤記錄
```http
DELETE /attendance?id=123456
```

### 獲取統計資訊
```http
GET /stats
```

**回應範例**:
```json
{
  "today_count": 25,
  "total_count": 1234,
  "latest_date": "2025-12-29"
}
```

### 健康檢查
```http
GET /health
```

---

## 📁 專案結構

```
attendance/
├── app.py                 # Flask 後端 API
├── gunicorn_config.py     # Gunicorn 配置
├── requirements.txt       # Python 依賴套件
├── index.html            # 前端介面
├── Dockerfile            # Docker 映像檔配置
├── build.sh              # 建置與執行腳本
├── nginx.conf            # Nginx 配置
├── .env.example          # 環境變數範例
└── README.md             # 本文件
```

---

## 🛠️ 開發指南

### 本地開發環境

```bash
# 安裝依賴
pip install -r requirements.txt

# 確保 MongoDB 運行中
mongod --dbpath /path/to/data

# 啟動開發伺服器
python app.py

# 或使用 Gunicorn
gunicorn -c gunicorn_config.py app:app
```

### 環境變數

複製 `.env.example` 為 `.env` 並修改配置：

```bash
cp .env.example .env
```

### Docker 指令參考

```bash
# 查看容器狀態
docker ps

# 查看容器日誌
docker logs -f attendance-app

# 進入容器
docker exec -it attendance-app bash

# 停止容器
docker stop attendance-app

# 啟動容器
docker start attendance-app

# 重啟容器
docker restart attendance-app

# 移除容器
docker rm attendance-app

# 移除映像檔
docker rmi attendance-app
```

---

## 💾 維護與備份

### 資料備份

資料存儲在 Docker Volume `attendance-data` 中：

```bash
# 備份資料
docker run --rm \
  -v attendance-data:/data \
  -v $(pwd):/backup \
  ubuntu tar cvf /backup/attendance-backup.tar /data

# 還原資料
docker run --rm \
  -v attendance-data:/data \
  -v $(pwd):/backup \
  ubuntu tar xvf /backup/attendance-backup.tar -C /
```

### 查看資料庫

```bash
# 進入容器
docker exec -it attendance-app bash

# 連接 MongoDB
mongosh

# 使用資料庫
use attendance

# 查看所有記錄
db.attendance.find()

# 查看統計
db.attendance.countDocuments()
```

### 日誌管理

```bash
# 即時查看日誌
docker logs -f attendance-app

# 查看最近 100 行
docker logs --tail 100 attendance-app

# 儲存日誌到檔案
docker logs attendance-app > app.log
```

---

## 🔧 故障排除

### 容器無法啟動

```bash
# 檢查容器日誌
docker logs attendance-app

# 檢查端口佔用
lsof -i :80
lsof -i :5050
```

### MongoDB 連線失敗

```bash
# 檢查 MongoDB 是否運行
docker exec attendance-app ps aux | grep mongod

# 重啟容器
docker restart attendance-app
```

### 前端無法連接 API

檢查 `index.html` 中的 `apiUrl` 是否正確設定為您的伺服器地址。

---

## 📄 授權

本專案僅供高榮禮拜堂內部使用。

---

## 👥 聯絡資訊

如有問題或建議，請聯繫系統管理員。

---

<div align="center">

**Built with ❤️ for 高榮禮拜堂**

</div>
