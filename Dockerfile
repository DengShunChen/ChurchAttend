# 多階段建置 Dockerfile - 優化版本
# Multi-stage Dockerfile - Optimized Version

# ===== Stage 1: Base Image =====
FROM python:3.9-slim as base

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ===== Stage 2: Python Dependencies =====
FROM base as python-deps

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# ===== Stage 3: MongoDB Installation =====
FROM python-deps as mongodb

# 安裝 MongoDB
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor && \
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org && \
    echo "mongodb-org hold" | dpkg --set-selections && \
    echo "mongodb-org-database hold" | dpkg --set-selections && \
    echo "mongodb-org-server hold" | dpkg --set-selections && \
    echo "mongodb-mongosh hold" | dpkg --set-selections && \
    echo "mongodb-org-mongos hold" | dpkg --set-selections && \
    echo "mongodb-org-tools hold" | dpkg --set-selections && \
    mkdir -p /data/db && \
    rm -rf /var/lib/apt/lists/*

# ===== Stage 4: Final Image =====
FROM mongodb as final

# 安裝 Nginx
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/*

# 複製應用程式檔案
COPY app.py .
COPY gunicorn_config.py .
COPY index.html .
COPY nginx.conf /etc/nginx/sites-available/default

# 建立啟動腳本
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# 啟動 MongoDB\n\
mongod --fork --logpath /var/log/mongodb.log\n\
\n\
# 等待 MongoDB 啟動\n\
sleep 3\n\
\n\
# 啟動 Nginx\n\
service nginx start\n\
\n\
# 使用 Gunicorn 啟動 Flask 應用（生產環境）\n\
exec gunicorn -c gunicorn_config.py app:app\n\
' > /app/start.sh && chmod +x /app/start.sh

# 設定環境變數
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 80 5050

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5050/health || exit 1

# 啟動應用
CMD ["/app/start.sh"]
