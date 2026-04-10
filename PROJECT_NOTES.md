# 專案備註 / Project Notes

## 🐳 容器化架構說明 (Containerization Architecture)

本專案採用完整的 Docker 容器化架構，以確保開發與生產環境的一致性，並簡化部署流程。

### 服務組件 (Services)

系統由三個主要容器服務組成，透過 `docker-compose` 進行編排：

1.  **應用伺服器 (App Server)**
    -   **Image**: `attendance-app` (基於 Python 3.9-slim)
    -   **角色**: 核心後端 API，使用 Flask 框架。
    -   **優化**: 使用多階段構建 (Multi-stage build) 縮減映像檔大小，並以非 root 用戶運行以提升安全性。
    -   **連接埠**: 內部與 Nginx 溝通，外部可選暴露 5050。

2.  **資料庫 (Database)**
    -   **Image**: `mongo:7.0`
    -   **角色**: 儲存所有出勤、會友與訪客資料。
    -   **持久化**: 使用 Docker Volume `attendance-mongodb-data` 確保資料重啟不遺失。
    -   **連接埠**: 內部 27017。

3.  **反向代理 (Reverse Proxy)**
    -   **Image**: `nginx:alpine`
    -   **角色**: 靜態資源伺服器與 API 轉發。
    -   **功能**:
        -   服務前端靜態檔案 (HTML, CSS, JS)。
        -   將 `/api` 請求轉發至 App Server。
    -   **連接埠**: 對外暴露 80 port。

---

## 🚀 啟動與操作 (Startup & Operations)

### 快速啟動
我們提供了自動化腳本來簡化操作：

```bash
# 一鍵建置並啟動所有服務
./build_compose.sh
```

此腳本會執行以下動作：
1. 清理舊容器
2. 重新建置映像檔
3. 啟動服務群組
4. 檢查服務健康狀態

### 常用 Docker 指令

- **查看服務狀態**:
  ```bash
  docker-compose ps
  ```

- **查看即時日誌**:
  ```bash
  docker-compose logs -f
  ```

- **停止服務**:
  ```bash
  docker-compose down
  ```

- **進入容器 (Ex: App)**:
  ```bash
  docker exec -it attendance-app bash
  ```

---

## 📂 檔案結構映射 (Volume Mapping)

為了開發便利，部分目錄已掛載至容器中：

- `./:/app`: 應用程式代碼 (支援熱重載)
- `./nginx/nginx.conf`: Nginx 設定檔
- `./static`: 前端靜態資源
- `attendance-mongodb-data`: 資料庫持久化儲存 (Docker Volume)

---

## ⚠️ 注意事項

1.  **環境變數**: 敏感資訊 (如 `QR_SECRET_KEY`) 儲存於 `.env` 檔案中，請勿提交至版本控制。
2.  **網絡隔離**: 所有服務運作於 `attendance-network` 內部網路，僅必要端口對外開放。
3.  **生產環境**: 部署時請確保 `FLASK_ENV=production` 並修改預設密鑰。
