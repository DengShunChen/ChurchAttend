# database.py
# MongoDB 資料庫連接管理
# MongoDB Database Connection Manager

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """MongoDB 資料庫管理類"""
    
    _instance: Optional['Database'] = None
    _client: Optional[MongoClient] = None
    _db = None
    
    def __new__(cls):
        """單例模式"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化時不建立連接，使用 lazy initialization"""
        pass
    
    def connect(self, uri: str, db_name: str, max_pool_size: int = 50,
                min_pool_size: int = 10, timeout_ms: int = 5000):
        """
        建立資料庫連接
        Establish database connection
        
        Args:
            uri: MongoDB 連接 URI
            db_name: 資料庫名稱
            max_pool_size: 連接池最大連接數
            min_pool_size: 連接池最小連接數
            timeout_ms: 連接超時時間（毫秒）
        """
        if self._client is not None:
            logger.warning("Database already connected, skipping connection")
            return
        
        try:
            self._client = MongoClient(
                uri,
                maxPoolSize=max_pool_size,
                minPoolSize=min_pool_size,
                serverSelectionTimeoutMS=timeout_ms,
                connectTimeoutMS=timeout_ms,
                socketTimeoutMS=timeout_ms * 2,
                retryWrites=True,
                retryReads=True
            )
            
            # 測試連接
            self._client.server_info()
            self._db = self._client[db_name]
            
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
            
            # 建立索引
            self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """
        關閉資料庫連接
        Close database connection
        """
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Database connection closed")
    
    @property
    def db(self):
        """
        取得資料庫實例
        Get database instance
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db
    
    @property
    def client(self):
        """
        取得客戶端實例
        Get client instance
        """
        if self._client is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._client
    
    def is_connected(self) -> bool:
        """
        檢查是否已連接
        Check if connected
        """
        if self._client is None:
            return False
        
        try:
            self._client.server_info()
            return True
        except Exception:
            return False
    
    def _create_indexes(self):
        """
        建立資料庫索引
        Create database indexes
        """
        try:
            # 出勤記錄索引
            # Attendance indexes
            self._db.attendance.create_index([("date", DESCENDING)])
            self._db.attendance.create_index([("name", ASCENDING)])
            self._db.attendance.create_index([("member_id", ASCENDING)])
            self._db.attendance.create_index([("session", ASCENDING)])
            
            # 複合索引 - 用於防止重複報到和快速查詢
            # Compound indexes - for duplicate prevention and fast queries
            self._db.attendance.create_index([("date", ASCENDING), ("name", ASCENDING)], unique=False)
            self._db.attendance.create_index([("date", ASCENDING), ("member_id", ASCENDING)], unique=False)
            self._db.attendance.create_index([("date", ASCENDING), ("session", ASCENDING)])
            
            # 會友資料索引
            # Member indexes
            self._db.members.create_index([("name", ASCENDING)], unique=True)
            self._db.members.create_index([("phone", ASCENDING)])
            self._db.members.create_index([("group", ASCENDING)])
            
            # 訪客資料索引
            # Visitor indexes
            self._db.visitors.create_index([("phone", ASCENDING)])
            self._db.visitors.create_index([("first_visit_date", DESCENDING)])
            self._db.visitors.create_index([("name", ASCENDING)])
            
            # 用戶認證索引（如果實作認證系統）
            # User authentication indexes (if implementing auth system)
            if "users" in self._db.list_collection_names():
                self._db.users.create_index([("username", ASCENDING)], unique=True)
                self._db.users.create_index([("email", ASCENDING)], unique=True)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise
    
    @contextmanager
    def session(self):
        """
        提供事務支援的 session context manager
        Session context manager with transaction support
        """
        session = self.client.start_session()
        try:
            yield session
        finally:
            session.end_session()
    
    def get_collection(self, name: str):
        """
        取得集合
        Get collection
        
        Args:
            name: 集合名稱
        
        Returns:
            Collection 對象
        """
        return self.db[name]
    
    def health_check(self) -> dict:
        """
        健康檢查
        Health check
        
        Returns:
            健康狀態資訊
        """
        try:
            if not self.is_connected():
                return {
                    'status': 'unhealthy',
                    'message': 'Database not connected'
                }
            
            # 取得伺服器狀態
            server_status = self._db.command('serverStatus')
            
            return {
                'status': 'healthy',
                'database': self._db.name,
                'connections': server_status.get('connections', {}),
                'uptime': server_status.get('uptime', 0)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': str(e)
            }


# 全域資料庫實例
# Global database instance
db_manager = Database()


def get_db():
    """
    取得資料庫實例（用於依賴注入）
    Get database instance (for dependency injection)
    """
    return db_manager.db
