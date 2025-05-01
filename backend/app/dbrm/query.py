class Condition:
    
    @staticmethod
    def eq(column, value):
        value_str = f"'{value}'" if isinstance(value, str) else str(value)
        return f"{column} = {value_str}"
    
    @staticmethod
    def ne(column, value):
        value_str = f"'{value}'" if isinstance(value, str) else str(value)
        return f"{column} != {value_str}"
    
    @staticmethod
    def gt(column, value):
        return f"{column} > {value}"
    
    @staticmethod
    def gte(column, value):
        return f"{column} >= {value}"
    
    @staticmethod
    def lt(column, value):
        return f"{column} < {value}"
    
    @staticmethod
    def lte(column, value):
        return f"{column} <= {value}"
    
    @staticmethod
    def like(column, pattern):
        return f"{column} LIKE '{pattern}'"
    
    @staticmethod
    def in_(column, values):
        formatted_values = []
        for v in values:
            if isinstance(v, str):
                formatted_values.append(f"'{v}'")
            else:
                formatted_values.append(str(v))
        return f"{column} IN ({', '.join(formatted_values)})"
    
    @staticmethod
    def between(column, start, end):
        return f"{column} BETWEEN {start} AND {end}"
    
    @staticmethod
    def is_null(column):
        return f"{column} IS NULL"
    
    @staticmethod
    def not_null(column):
        return f"{column} IS NOT NULL"
    
    @staticmethod
    def or_(*conditions):
        return f"({' OR '.join(conditions)})"
    
    @staticmethod
    def and_(*conditions):
        return f"({' AND '.join(conditions)})"


class Select:
    
    def __init__(self, *columns, session=None):
        self.columns = columns or ["*"]
        self.from_table = None
        self.where_clauses = []
        self.order_by_columns = []
        self.limit_count = None
        self.offset_count = None
        self.group_by_columns = []
        self.having_clauses = []
        self.join_clauses = []
        self._params = []
        self._model_class = None
        self._session = session
    
    def from_(self, table):
        if hasattr(table, '__tablename__'):
            self.from_table = table.__tablename__
            self._model_class = table
        else:
            self.from_table = table
        return self
    
    def where(self, condition):
        self.where_clauses.append(condition)
        return self
        
    def filter_by(self, **kwargs):
        for column, value in kwargs.items():
            condition = Condition.eq(column, value)
            self.where_clauses.append(condition)
        return self
    
    def order_by(self, *columns):
        self.order_by_columns.extend(columns)
        return self
        
    def order_by_asc(self, column):
        self.order_by_columns.append(f"{column} ASC")
        return self
        
    def order_by_desc(self, column):
        self.order_by_columns.append(f"{column} DESC")
        return self
    
    def limit(self, count):
        self.limit_count = count
        return self
    
    def offset(self, count):
        self.offset_count = count
        return self
    
    def group_by(self, *columns):
        self.group_by_columns.extend(columns)
        return self
    
    def having(self, condition):
        self.having_clauses.append(condition)
        return self
    
    def join(self, table, condition, join_type="INNER"):
        if hasattr(table, '__tablename__'):
            table_name = table.__tablename__
        else:
            table_name = table
        self.join_clauses.append((join_type, table_name, condition))
        return self
        
    def left_join(self, table, condition):
        return self.join(table, condition, "LEFT")
        
    def right_join(self, table, condition):
        return self.join(table, condition, "RIGHT")
        
    def full_join(self, table, condition):
        return self.join(table, condition, "FULL")
    
    def build(self):
        if not self.from_table:
            raise ValueError("No FROM table specified")
        
        columns = ", ".join(str(col) for col in self.columns)
        sql = f"SELECT {columns} FROM {self.from_table}"
        
        for join_type, table, condition in self.join_clauses:
            sql += f" {join_type} JOIN {table} ON {condition}"
        
        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)
        
        if self.group_by_columns:
            sql += " GROUP BY " + ", ".join(self.group_by_columns)
        
        if self.having_clauses:
            sql += " HAVING " + " AND ".join(self.having_clauses)
        
        if self.order_by_columns:
            sql += " ORDER BY " + ", ".join(self.order_by_columns)
        
        if self.limit_count is not None:
            sql += f" LIMIT {self.limit_count}"
        
        if self.offset_count is not None:
            sql += f" OFFSET {self.offset_count}"
        
        return sql
    
    def execute(self, session=None):
        session = session or self._session
        if not session:
            raise ValueError("No session provided for query execution")
        sql = self.build()
        return session.execute(sql)
        
    def first(self, session=None):
        session = session or self._session
        if not session:
            raise ValueError("No session provided for query execution")
        self.limit(1)
        self.execute(session)
        row = session.fetchone()
        
        if not row:
            return None
            
        if self._model_class and hasattr(self._model_class, '_from_row'):
            return self._model_class._from_row(row)
        return row
        
    def all(self, session=None):
        session = session or self._session
        if not session:
            raise ValueError("No session provided for query execution")
        self.execute(session)
        rows = session.fetchall()
        
        if self._model_class and hasattr(self._model_class, '_from_row'):
            return [self._model_class._from_row(row) for row in rows]
        return rows
    
    def count(self, session=None):
        session = session or self._session
        if not session:
            raise ValueError("No session provided for query execution")
        original_columns = self.columns
        self.columns = ["COUNT(*)"]
        self.execute(session)
        result = session.fetchone()
        self.columns = original_columns
        return result[0] if result else 0
    
    def exists(self, session):
        return self.limit(1).count(session) > 0
    
    def __str__(self):
        return self.build()


class Insert:
    
    def __init__(self, table=None):
        self.table = table.__tablename__ if hasattr(table, '__tablename__') else table
        self.columns = []
        self.values = []
        self.returning = None
        
    def into(self, table):
        self.table = table.__tablename__ if hasattr(table, '__tablename__') else table
        return self
        
    def columns_(self, *cols):
        self.columns = cols
        return self
        
    def values_(self, *vals):
        self.values.append(vals)
        return self
        
    def returning_(self, *cols):
        self.returning = cols
        return self
        
    def build(self):
        if not self.table:
            raise ValueError("No table specified for INSERT")
        if not self.columns:
            raise ValueError("No columns specified for INSERT")
        if not self.values:
            raise ValueError("No values specified for INSERT")
            
        cols = ", ".join(self.columns)
        
        all_values = []
        for row in self.values:
            row_values = []
            for val in row:
                if val is None:
                    row_values.append("NULL")
                elif isinstance(val, str):
                    row_values.append(f"'{val}'")
                else:
                    row_values.append(str(val))
            all_values.append(f"({', '.join(row_values)})")
            
        values_str = ", ".join(all_values)
        
        sql = f"INSERT INTO {self.table} ({cols}) VALUES {values_str}"
        
        if self.returning:
            sql += " RETURNING " + ", ".join(self.returning)
            
        return sql
    
    def execute(self, session):
        return session.execute(self.build())
        
    def __str__(self):
        return self.build()


class Update:
    
    def __init__(self, table=None):
        self.table = table.__tablename__ if hasattr(table, '__tablename__') else table
        self.set_clauses = {}
        self.where_clauses = []
        
    def table_(self, table):
        self.table = table.__tablename__ if hasattr(table, '__tablename__') else table
        return self
        
    def set_(self, **kwargs):
        self.set_clauses.update(kwargs)
        return self
        
    def where(self, condition):
        self.where_clauses.append(condition)
        return self
        
    def filter_by(self, **kwargs):
        for column, value in kwargs.items():
            condition = Condition.eq(column, value)
            self.where_clauses.append(condition)
        return self
        
    def build(self):
        if not self.table:
            raise ValueError("No table specified for UPDATE")
        if not self.set_clauses:
            raise ValueError("No SET clauses specified for UPDATE")
            
        set_parts = []
        for col, val in self.set_clauses.items():
            if val is None:
                set_parts.append(f"{col} = NULL")
            elif isinstance(val, str):
                set_parts.append(f"{col} = '{val}'")
            else:
                set_parts.append(f"{col} = {val}")
                
        set_sql = ", ".join(set_parts)
        
        sql = f"UPDATE {self.table} SET {set_sql}"
        
        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)
            
        return sql
    
    def execute(self, session):
        return session.execute(self.build())
        
    def __str__(self):
        return self.build()


class Delete:
    
    def __init__(self, table=None):
        self.table = table.__tablename__ if hasattr(table, '__tablename__') else table
        self.where_clauses = []
        
    def from_(self, table):
        self.table = table.__tablename__ if hasattr(table, '__tablename__') else table
        return self
        
    def where(self, condition):
        self.where_clauses.append(condition)
        return self
        
    def filter_by(self, **kwargs):
        for column, value in kwargs.items():
            condition = Condition.eq(column, value)
            self.where_clauses.append(condition)
        return self
        
    def build(self):
        if not self.table:
            raise ValueError("No table specified for DELETE")
            
        sql = f"DELETE FROM {self.table}"
        
        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)
            
        return sql
    
    def execute(self, session):
        return session.execute(self.build())
        
    def __str__(self):
        return self.build()
