import pyodbc
import os
from contextlib import contextmanager
from dotenv import load_dotenv

class Engine:
    """Database engine that manages connections."""
    
    def __init__(self, connection_string=None, **kwargs):
        self.connection_string = connection_string
        self._connection_params = kwargs
        
    @classmethod
    def from_env(cls):
        """Create engine from environment variables."""
        load_dotenv()
        
        connection_string = (
            f'DRIVER={{{os.getenv("DRIVER", "ODBC Driver 17 for SQL Server")}}};'
            f'SERVER={os.getenv("SERVER")};'
            f'DATABASE={os.getenv("DATABASE")};'
            f'UID={os.getenv("UID")};'
            f'PWD={os.getenv("PWD")};'
            'charset=utf8mb4;'
        )
        return cls(connection_string)
    
    def connect(self):
        """Get a connection."""
        conn = pyodbc.connect(self.connection_string)
        conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
        conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        conn.setencoding(encoding='utf-8')
        return conn
    
    @contextmanager
    def begin(self):
        """Get a connection as a context manager."""
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()
            
    def execute_raw(self, sql, params=None):
        """执行原始SQL并返回结果。"""
        with self.begin() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                    
                if sql.strip().upper().startswith(("SELECT", "SHOW", "DESC")):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                conn.rollback()
                raise
            finally:
                cursor.close()
                
    def create_session(self):
        """创建新会话。"""
        from .session import Session
        return Session(self)
