import sqlite3
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库，创建历史记录表"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 创建历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    preset TEXT NOT NULL DEFAULT 'speed',
                    steps INTEGER NOT NULL DEFAULT 10,
                    guidance REAL NOT NULL DEFAULT 5.0,
                    octree_resolution INTEGER NOT NULL DEFAULT 192
                )
            ''')
            # 创建timestamp字段索引，优化ORDER BY timestamp DESC查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp DESC)
            ''')
            conn.commit()
    
    def add_history(self, history_data: Dict) -> bool:
        """添加历史记录"""
        # 验证必填字段
        required_fields = ['id', 'filename', 'model_path', 'timestamp']
        for field in required_fields:
            if field not in history_data or history_data[field] is None:
                logger.error(f"Error adding history: Missing required field '{field}'")
                return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO history (id, filename, model_path, timestamp, preset, steps, guidance, octree_resolution)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    history_data['id'],
                    history_data['filename'],
                    history_data['model_path'],
                    history_data['timestamp'],
                    history_data.get('preset'),
                    history_data.get('steps'),
                    history_data.get('guidance'),
                    history_data.get('octree_resolution')
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Database error adding history: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding history: {e}")
            return False
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史记录列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM history
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    def delete_history(self, history_id: str) -> bool:
        """删除历史记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM history WHERE id = ?
                ''', (history_id,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting history: {e}")
            return False
    
    def get_history_by_id(self, history_id: str) -> Optional[Dict]:
        """根据 ID 获取历史记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM history WHERE id = ?
                ''', (history_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error getting history by id: {e}")
            return None

# 单例模式管理数据库实例
db_instance = None

def get_db() -> Database:
    """获取数据库实例（单例模式）"""
    global db_instance
    if db_instance is None:
        db_path = Path(__file__).resolve().parent.parent / "data" / "history.db"
        db_instance = Database(str(db_path))
    return db_instance
