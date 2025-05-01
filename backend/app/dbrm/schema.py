from typing import TypeVar

T = TypeVar('T')

class Column:
    """Represents a database column."""
    
    def __init__(self, type_=None, primary_key=False, nullable=True, 
                 unique=False, default=None, autoincrement=False, 
                 foreign_key=None, on_delete=None, on_update=None,
                 comment=None, index=False, check=None):
        """
        Create a database column definition.
        
        Args:
            type_: Column data type
            primary_key: Whether it's a primary key
            nullable: Whether it allows NULL values
            unique: Whether the column has a unique constraint
            default: Default value
            autoincrement: Whether the column auto-increments
            foreign_key: Foreign key relationship (table.column, table(column) or just table name)
            on_delete: ON DELETE action (CASCADE, SET NULL, RESTRICT, NO ACTION)
            on_update: ON UPDATE action (CASCADE, SET NULL, RESTRICT, NO ACTION)
            comment: Column comment
            index: Whether to create an index
            check: CHECK constraint (e.g., "BETWEEN 1 AND 5" or "IN ('Customer', 'Worker', 'Administrator')")
        """
        self.type = type_
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        self.default = default
        self.autoincrement = autoincrement
        self.foreign_key = foreign_key
        self.on_delete = on_delete
        self.on_update = on_update
        self.comment = comment
        self.index = index
        self.check = check
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
        pk_columns = []
        
        for name, column in cls._columns.items():
            sql_type = column.type.__name__ if hasattr(column.type, '__name__') else str(column.type)
                
            nullable = "NOT NULL" if not column.nullable else "NULL"
            autoinc = "AUTO_INCREMENT" if column.autoincrement else ""
            unique = "UNIQUE" if column.unique else ""
            default = f"DEFAULT {column.default}" if column.default is not None else ""
            comment = f"COMMENT '{column.comment}'" if column.comment else ""
            check = f"CHECK ({name} {column.check})" if column.check else ""
            
            column_def = f"{name} {sql_type} {nullable} {autoinc} {unique} {default} {check} {comment}".strip()
            columns.append(column_def)
            
            if column.primary_key:
                pk_columns.append(name)
            
            if column.foreign_key:
                # "table.column" | "table(column)"
                if "(" in column.foreign_key and ")" in column.foreign_key:
                    # table(column)
                    table_name, ref_column = column.foreign_key.split("(")
                    ref_column = ref_column.rstrip(")")
                    fk_def = f"FOREIGN KEY ({name}) REFERENCES {table_name}({ref_column})"
                elif "." in column.foreign_key:
                    # table.column
                    table_name, ref_column = column.foreign_key.split(".")
                    fk_def = f"FOREIGN KEY ({name}) REFERENCES {table_name}({ref_column})"
                else:
                    raise ValueError(f"Invalid foreign key format: {column.foreign_key}")
                
                if hasattr(column, 'on_delete') and column.on_delete:
                    fk_def += f" ON DELETE {column.on_delete}"
                if hasattr(column, 'on_update') and column.on_update:
                    fk_def += f" ON UPDATE {column.on_update}"
                    
                foreign_keys.append(fk_def)
            
            if column.index and not column.primary_key:
                index_def = f"INDEX idx_{cls.__tablename__}_{name} ({name})"
                indexes.append(index_def)
        
        if pk_columns:
            pk_def = f"PRIMARY KEY ({', '.join(pk_columns)})"
            columns.append(pk_def)
        
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
    def _get_primary_key_info(cls):
        pk_names = []
        
        for name, column in cls._columns.items():
            if column.primary_key:
                pk_names.append(name)
        
        if not pk_names:
            raise ValueError(f"No primary key defined for table {cls.__tablename__}")
            
        return pk_names
    
    def _get_primary_key_value(self):
        pk_names = self.__class__._get_primary_key_info()
        pk_values = {}
        
        for pk_name in pk_names:
            pk_value = getattr(self, pk_name, None)
            if pk_value is None:
                raise ValueError(f"Primary key column '{pk_name}' has None value")
            pk_values[pk_name] = pk_value
            
        return pk_values
    
    @classmethod
    def get(cls, session, *args, **kwargs):
        """
        Get a single record by primary key(s)
        
        - Model.get(session, id_value)
        - Model.get(session, column1=value1, column2=value2)
        """
        pk_columns = cls._get_primary_key_info()
        
        from .query import Select, Condition
        query = Select(session=session).from_(cls)
        
        if args and len(args) == 1 and len(pk_columns) == 1:
            query.where(Condition.eq(pk_columns[0], args[0]))
        elif kwargs:
            for column, value in kwargs.items():
                query.where(Condition.eq(column, value))
        else:
            raise ValueError("Please provide primary key value(s)")
            
        return query.limit(1).first()
    
    @classmethod
    def get_all(cls, session, limit=None, offset=None):
        """Get all records"""
        from .query import Select
        
        query = Select(session=session).from_(cls)
        
        if limit is not None:
            query.limit(limit)
        if offset is not None:
            query.offset(offset)
            
        return query.all()
    
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
        pk_values = self._get_primary_key_value()
        pk_names = self.__class__._get_primary_key_info()
        
        from .query import Select, Condition
        exists_query = Select(session=session).from_(self.__class__)
        
        for name, value in pk_values.items():
            exists_query.where(Condition.eq(name, value))
        
        exists = exists_query.limit(1).exists()
        
        data = {}
        for name, column in self.__class__._columns.items():
            value = getattr(self, name, None)
            if value is not None:
                data[name] = value
        
        if exists:
            from .query import Update, Condition
            
            update_data = {k: v for k, v in data.items() if k not in pk_names}
            
            if update_data:
                update_query = Update().table_(self.__class__.__tablename__).set_(**update_data)
                
                for name, value in pk_values.items():
                    update_query.where(Condition.eq(name, value))
                
                session.execute(update_query)
                session.commit()
        else:
            from .query import Insert
            
            insert_query = Insert().into(self.__class__.__tablename__).columns_(*data.keys()).values_(*data.values())
            session.execute(insert_query)
            session.commit()
        
        return self
    
    def delete(self, session):
        """Delete object from database"""
        pk_values = self._get_primary_key_value()
        
        from .query import Delete, Condition
        
        delete_query = Delete().from_(self.__class__.__tablename__)
        
        for name, value in pk_values.items():
            delete_query.where(Condition.eq(name, value))
        
        session.execute(delete_query)
        session.commit()
        return True
        
Table = TableBase