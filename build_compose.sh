#!/bin/bash
# build_compose.sh
# Docker Compose 建置與執行腳本
# Docker Compose Build and Run Script

set -e

echo "🏗️  使用 Docker Compose 建置系統..."
echo "Building system with Docker Compose..."

# 停止並移除現有容器
echo "🧹 清理現有容器..."
docker-compose down 2>/dev/null || true

# 建置映像
echo "📦 建置映像..."
docker-compose build

# 啟動服務
echo "🚀 啟動服務..."
docker-compose up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 5

# 檢查服務狀態
echo "📊 服務狀態:"
docker-compose ps

echo ""
echo "✅ 系統啟動完成！"
echo "System startup complete!"
echo ""
echo "📍 存取資訊 / Access Information:"
echo "   前端介面 / Frontend: http://localhost"
echo "   API 端點 / API: http://localhost:5050"
echo "   健康檢查 / Health:  http://localhost:5050/health"
echo ""
echo "📊 查看日誌 / View logs:"
echo "   所有服務 / All: docker-compose logs -f"
echo "   應用 / App: docker-compose logs -f app"
echo "   資料庫 / DB: docker-compose logs -f mongodb"
echo ""
echo "🛑 停止系統 / Stop system:"
echo "   docker-compose down"
