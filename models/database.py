import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv(encoding='utf-8')

# 配置日志
logger = logging.getLogger('collector')

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                charset='utf8mb4',
                cursorclass=DictCursor,
                use_unicode=True
            )
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise

    def execute(self, sql, params=None):
        """执行SQL语句"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            logger.error(f"SQL执行失败: {str(e)}")
            raise

    def executemany(self, sql, params_list):
        """批量执行SQL语句"""
        try:
            with self.conn.cursor() as cursor:
                cursor.executemany(sql, params_list)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            logger.error(f"批量SQL执行失败: {str(e)}")
            raise

    def fetch_all(self, sql, params=None):
        """查询多条数据"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

    def fetch_one(self, sql, params=None):
        """查询单条数据"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()

    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except Exception:
                pass  # 忽略关闭时的错误
            finally:
                self.conn = None

    def __del__(self):
        """析构函数，确保关闭数据库连接"""
        self.close() 