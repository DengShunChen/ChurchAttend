# Gunicorn 配置檔案
# Gunicorn Configuration File

import multiprocessing

# 綁定地址和端口
# Bind address and port
bind = "0.0.0.0:5050"

# Worker 進程數量 (建議為 CPU 核心數的 2-4 倍)
# Number of worker processes (recommended: 2-4x CPU cores)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 類別 (sync 適合 I/O 密集型應用)
# Worker class (sync is good for I/O-bound applications)
worker_class = "sync"

# 每個 worker 的執行緒數
# Number of threads per worker
threads = 2

# Worker 超時時間 (秒)
# Worker timeout in seconds
timeout = 30

# 最大請求數，之後 worker 會重啟 (防止記憶體洩漏)
# Max requests before worker restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# 優雅重啟超時
# Graceful timeout
graceful_timeout = 30

# 保持連線
# Keep alive
keepalive = 5

# 日誌等級
# Log level
loglevel = "info"

# 訪問日誌格式
# Access log format
accesslog = "-"  # 輸出到 stdout
errorlog = "-"   # 輸出到 stderr

# 預載應用 (可提升效能但使用更多記憶體)
# Preload app (improves performance but uses more memory)
preload_app = True
