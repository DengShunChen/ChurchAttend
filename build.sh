#!/bin/bash
# 高榮禮拜堂出勤系統 - Docker 建置與執行腳本
# Church Attendance System - Docker Build and Run Script

set -e  # 遇到錯誤立即停止

echo "🏗️  正在建置 Docker 映像檔..."
echo "Building Docker image..."

# 建置 Docker 映像檔
docker build -t attendance-app .

echo "✅ 映像檔建置完成！"
echo "Image built successfully!"

# 停止並移除舊容器（如果存在）
echo "🧹 清理舊容器..."
echo "Cleaning up old containers..."
docker stop attendance-app 2>/dev/null || true
docker rm attendance-app 2>/dev/null || true

echo "🚀 正在啟動容器..."
echo "Starting container..."

# 啟動容器，加入資料持久化
docker run -d \
    --name attendance-app \
    -p 80:80 \
    -p 5050:5050 \
    -v attendance-data:/data/db \
    --restart unless-stopped \
    attendance-app:latest

echo "✅ 容器啟動成功！"
echo "Container started successfully!"
echo ""
echo "📍 存取資訊 / Access Information:"
echo "   前端介面 / Frontend: http://localhost"
echo "   API 端點 / API: http://localhost:5050"
echo "   健康檢查 / Health: http://localhost:5050/health"
echo ""
echo "📊 查看容器狀態 / View container status:"
echo "   docker ps"
echo ""
echo "📝 查看容器日誌 / View container logs:"
echo "   docker logs -f attendance-app"
echo ""
echo "🛑 停止容器 / Stop container:"
echo "   docker stop attendance-app"
