from contextlib import contextmanager
from typing import Any, List, Dict, Tuple, Optional, TypeVar
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .query import Select, Insert, Update, Delete

T = TypeVar('T')

logger = logging.getLogger(__name__)

class Session:
    
    def __init__(self, engine):
        self.engine = engine
        self._connection = None
        self._cursor = None
        self._transaction_level = 0
        self._in_transaction = False
        self._query_log = []
        
    def __enter__(self):
        self._connection = self.engine.connect()
        self._cursor = self._connection.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and self._in_transaction:
            try:
                self.rollback()
            except Exception as e:
                logger.error(f"Fail to rollback transaction: {e}") 
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()
            self._connection = None
            
    def log_query(self, query: str) -> None:
        self._query_log.append(query)
        if len(self._query_log) > 100:
            self._query_log = self._query_log[-100:]
            
    def get_query_log(self) -> List[str]:
        return self._query_log
        
    def execute(self, query, params=None):
        from .query import Select, Insert, Update, Delete
        
        if isinstance(query, (Select, Insert, Update, Delete)):
            query_str = str(query)
        else:
            query_str = query
            
        try:
            self.log_query(query_str)
            if params:
                self._cursor.execute(query_str, params)
            else:
                self._cursor.execute(query_str)
            return self._cursor
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            logger.error(f"Query: {query_str}")
            raise
    
    def fetchall(self) -> List[Tuple]:
        return self._cursor.fetchall()
    
    def fetchone(self) -> Optional[Tuple]:
        return self._cursor.fetchone()
        
    def scalar(self) -> Any:
        row = self.fetchone()
        return row[0] if row else None
        
    def fetch_as_dict(self) -> Optional[Dict]:
        row = self.fetchone()
        if not row:
            return None
            
        column_names = [desc[0] for desc in self._cursor.description]
        return dict(zip(column_names, row))
        
    def fetchall_as_dict(self) -> List[Dict]:
        results = self.fetchall()
        if not results:
            return []
            
        column_names = [desc[0] for desc in self._cursor.description]
        return [dict(zip(column_names, row)) for row in results]
    
    def commit(self):
        if self._connection:
            try:
                self._connection.commit()
                self._in_transaction = False
            except Exception as e:
                logger.error(f"Fail to commit transaction: {e}")
                raise
    
    def rollback(self):
        if self._connection:
            try:
                self._connection.rollback()
                self._in_transaction = False
            except Exception as e:
                logger.error(f"Fail to rollback transaction: {e}")
                raise

    @contextmanager
    def begin(self):
        self._transaction_level += 1
        if self._transaction_level == 1:
            self._connection.autocommit = False
            self._in_transaction = True
        try:
            yield self
            if self._transaction_level == 1:
                self.commit()
        except Exception as e:
            if self._transaction_level == 1:
                logger.error(f"Transaction failed: {e}")
                self.rollback()
            raise
        finally:
            self._transaction_level -= 1

    def query(self, col_or_model_class) -> 'Select':
        from .query import Select
        if hasattr(col_or_model_class, 'parent'):
            return Select(col_or_model_class, session=self).from__(col_or_model_class.parent)
        return Select(session=self).from_(col_or_model_class)

    def add(self, obj):
        if hasattr(obj, 'save'):
            obj.save(self)
        return self
        
    def delete(self, obj):
        if hasattr(obj, 'delete'):
            obj.delete(self)
        return self
    
    def refresh(self, obj):
        if hasattr(obj, 'refresh'):
            obj.refresh(self)
        return self
    
    def add_and_refresh(self, obj):
        self.add(obj)
        self.commit()
        return self.refresh(obj)
        
    def bulk_insert(self, table, data_list):
        if not data_list:
            return 0
            
        table_name = table.__tablename__ if hasattr(table, '__tablename__') else table
        
        columns = list(data_list[0].keys())
        
        from .query import Insert
        query = Insert().into(table_name).columns_(*columns)
        
        for data in data_list:
            values = [data.get(col) for col in columns]
            query.values_(*values)
            
        self.execute(query)
        self.commit()
        
        return len(data_list)
        
    def create_all(self, models):
        for model in models:
            if hasattr(model, 'create'):
                model.create(self)
                
    def drop_all(self, models):
        for model in models:
            if hasattr(model, 'drop'):
                model.drop(self)

