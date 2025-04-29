from .types import DTYPE_MAPPING, String, StringType, get_sql_type
from typing import Any, TypeVar, Optional, List, Dict, Generic, Type, Union

T = TypeVar('T')

class Column:
    """Represents a database column."""
    
    def __init__(self, type_=None, primary_key=False, nullable=True, 
                 unique=False, default=None, autoincrement=False, 
                 foreign_key=None, length=None, comment=None, index=False):
        """
        Create a database column definition.
        
        Args:
            type_: Column data type
            primary_key: Whether it's a primary key
            nullable: Whether it allows NULL values
            unique: Whether the column has a unique constraint
            default: Default value
            autoincrement: Whether the column auto-increments
            foreign_key: Foreign key relationship (table.column format)
            length: Length for string type
            comment: Column comment
            index: Whether to create an index
        """
        self.type = type_
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        self.default = default
        self.autoincrement = autoincrement
        self.foreign_key = foreign_key
        self.length = length
        self.comment = comment
        self.index = index
        self.name = None
        
    def __set_name__(self, owner, name):
        self.name = name


class Relationship:
    
    def __init__(self, target_model, foreign_key=None, backref=None, lazy='select', cascade=None):
        """
        Create table relationship.
        
        Args:
            target_model: Target model class or class name
            foreign_key: Foreign key column name
            backref: Back reference name
            lazy: Loading strategy ('select', 'joined', 'subquery')
            cascade: Cascade operations
        """
        self.target_model = target_model
        self.foreign_key = foreign_key
        self.backref = backref
        self.lazy = lazy
        self.cascade = cascade
        self.name = None
        self.parent = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.parent = owner


class TableBase:
    """Base class for all table definitions."""
    
    @classmethod
    def __init_subclass__(cls):
        cls.__tablename__ = getattr(cls, '__tablename__', cls.__name__.lower())
        cls._columns = {}
        cls._relationships = {}
        
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Column):
                attr.__set_name__(cls, name)
                cls._columns[name] = attr
            elif isinstance(attr, Relationship):
                attr.__set_name__(cls, name)
                cls._relationships[name] = attr
    
    @classmethod
    def create(cls, session):
        """Create this table in the database."""
        columns = []
        foreign_keys = []
        indexes = []
        
        for name, column in cls._columns.items():
            type_name = column.type.__name__ if hasattr(column.type, '__name__') else str(column.type)
            
            # Handle string type length settings
            if type_name == 'str' and column.length:
                sql_type = String(column.length)
            else:
                sql_type = DTYPE_MAPPING.get(type_name, String)
                
            nullable = "NOT NULL" if not column.nullable else "NULL"
            pk = "PRIMARY KEY" if column.primary_key else ""
            autoinc = "AUTO_INCREMENT" if column.autoincrement else ""
            unique = "UNIQUE" if column.unique else ""
            default = f"DEFAULT {column.default}" if column.default is not None else ""
            comment = f"COMMENT '{column.comment}'" if column.comment else ""
            
            column_def = f"{name} {sql_type} {nullable} {pk} {autoinc} {unique} {default} {comment}".strip()
            columns.append(column_def)
            
            if column.foreign_key:
                fk_def = f"FOREIGN KEY ({name}) REFERENCES {column.foreign_key}"
                foreign_keys.append(fk_def)
            
            if column.index and not column.primary_key:
                index_def = f"INDEX idx_{cls.__tablename__}_{name} ({name})"
                indexes.append(index_def)
        
        # Combine all column definitions and constraints
        all_defs = columns + foreign_keys + indexes
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {cls.__tablename__} (\n  " + ",\n  ".join(all_defs) + "\n)"
        session.execute(create_sql)
        session.commit()
        return True
    
    @classmethod
    def drop(cls, session):
        """Drop this table from the database."""
        drop_sql = f"DROP TABLE IF EXISTS {cls.__tablename__}"
        session.execute(drop_sql)
        session.commit()
        return True
        
    @classmethod
    def table_exists(cls, session):
        """Check if this table exists in the database."""
        try:
            session.execute(f"SELECT 1 FROM {cls.__tablename__} LIMIT 1")
            return True
        except Exception:
            return False
    
    @classmethod
    def get(cls, session, id_value):
        """Get a single record by primary key"""
        pk_column = None
        for name, column in cls._columns.items():
            if column.primary_key:
                pk_column = name
                break
        
        if not pk_column:
            raise ValueError(f"No primary key defined for table {cls.__tablename__}")
        
        id_value_str = f"'{id_value}'" if isinstance(id_value, str) else str(id_value)
        query = f"SELECT * FROM {cls.__tablename__} WHERE {pk_column} = {id_value_str}"
        
        session.execute(query)
        row = session.fetchone()
        if not row:
            return None
        
        return cls._from_row(row)
    
    @classmethod
    def get_all(cls, session, limit=None, offset=None):
        """Get all records"""
        query = f"SELECT * FROM {cls.__tablename__}"
        
        if limit is not None:
            query += f" LIMIT {limit}"
        if offset is not None:
            query += f" OFFSET {offset}"
            
        session.execute(query)
        rows = session.fetchall()
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create instance from database row"""
        if isinstance(row, tuple):
            column_names = list(cls._columns.keys())
            row_dict = dict(zip(column_names, row))
        else:
            row_dict = row
            
        instance = cls()
        for key, value in row_dict.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance
    
    def save(self, session):
        """Save instance to database (Insert or Update)"""
        pk_name = None
        pk_value = None
        
        for name, column in self.__class__._columns.items():
            if column.primary_key:
                pk_name = name
                pk_value = getattr(self, name, None)
                break
        
        if pk_value is None:
            raise ValueError("Cannot save object with None primary key")
        
        exists_query = f"SELECT 1 FROM {self.__class__.__tablename__} WHERE {pk_name} = "
        exists_query += f"'{pk_value}'" if isinstance(pk_value, str) else str(pk_value)
        
        session.execute(exists_query)
        exists = session.fetchone() is not None
        
        data = {}
        for name, column in self.__class__._columns.items():
            value = getattr(self, name, None)
            if value is not None:
                data[name] = value
        
        if exists:
            # Update
            set_clauses = []
            for name, value in data.items():
                if name != pk_name:
                    value_str = f"'{value}'" if isinstance(value, str) else str(value)
                    set_clauses.append(f"{name} = {value_str}")
                    
            if set_clauses:
                update_query = f"UPDATE {self.__class__.__tablename__} SET {', '.join(set_clauses)} WHERE {pk_name} = "
                update_query += f"'{pk_value}'" if isinstance(pk_value, str) else str(pk_value)
                session.execute(update_query)
                session.commit()
        else:
            # Insert
            columns = list(data.keys())
            values = []
            
            for value in data.values():
                if isinstance(value, str):
                    values.append(f"'{value}'")
                else:
                    values.append(str(value))
            
            insert_query = f"INSERT INTO {self.__class__.__tablename__} ({', '.join(columns)}) VALUES ({', '.join(values)})"
            session.execute(insert_query)
            session.commit()
        
        return self
    
    def delete(self, session):
        """Delete object from database"""
        pk_name = None
        pk_value = None
        
        for name, column in self.__class__._columns.items():
            if column.primary_key:
                pk_name = name
                pk_value = getattr(self, name, None)
                break
                
        if pk_value is None:
            raise ValueError("Cannot delete object with None primary key")
            
        delete_query = f"DELETE FROM {self.__class__.__tablename__} WHERE {pk_name} = "
        delete_query += f"'{pk_value}'" if isinstance(pk_value, str) else str(pk_value)
        
        session.execute(delete_query)
        session.commit()
        return True
        
# Create a base class for declarative table definitions
Table = TableBase
