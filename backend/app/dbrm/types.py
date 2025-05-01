"""
Database type definition module, providing SQL type mapping.
"""
from typing import Any

class SqlType:
    """SQL type base class, can be represented as a string"""
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return f"SqlType({self.name})"


class StringType(SqlType):
    """VARCHAR type, supports specifying length"""
    def __init__(self, length=255):
        self.length = length
        super().__init__(f"VARCHAR({length})")
    
    def __call__(self, length):
        """Supports usage like String(50)"""
        return StringType(length)


class NumericType(SqlType):
    """NUMERIC type, supports specifying precision and scale"""
    def __init__(self, precision=10, scale=2):
        self.precision = precision
        self.scale = scale
        super().__init__(f"NUMERIC({precision},{scale})")
    
    def __call__(self, precision, scale=2):
        """Supports usage like Numeric(15,4)"""
        return NumericType(precision, scale)


Integer = SqlType('INTEGER')
Float = SqlType('FLOAT')
Double = SqlType('DOUBLE')
Boolean = SqlType('BOOLEAN')
String = StringType()
Text = SqlType('TEXT')
DateTime = SqlType('DATETIME')
Date = SqlType('DATE')
Time = SqlType('TIME')
Timestamp = SqlType('TIMESTAMP')
JSON = SqlType('TEXT')
BLOB = SqlType('BLOB')
LongText = SqlType('LONGTEXT')
SmallInt = SqlType('SMALLINT')
BigInt = SqlType('BIGINT')
Decimal = SqlType('DECIMAL')
Numeric = NumericType()
Interval = SqlType('INTERVAL')

DTYPE_MAPPING = {
    'int64': Integer,
    'int32': Integer,
    'int16': Integer,
    'int8': Integer,
    'uint64': Integer,
    'uint32': Integer,
    'uint16': Integer,
    'uint8': Integer,
    'float64': Double,
    'float32': Float,
    'float16': Float,
    'int': Integer,
    'float': Float,
    'bool': Boolean,
    'str': String,
    'datetime64[ns]': DateTime,
    'datetime64': DateTime,
    'timedelta64': Interval,
    'datetime': DateTime,
    'date': Date,
    'object': String,
    'category': String,
    'dict': JSON,
    'list': JSON,
    'json': JSON,
    'bytes': BLOB,
    'text': Text,
    'longtext': LongText,
    'smallint': SmallInt,
    'bigint': BigInt,
    'decimal': Decimal,
    'numeric': Numeric,
    'time': Time,
    'timestamp': Timestamp,
}


def get_sql_type(python_type: Any) -> str:
    """
    Get the corresponding SQL type string based on Python type.
    
    Args:
        python_type: Python type or type name
    
    Returns:
        str: SQL type string
    """
    if isinstance(python_type, (SqlType, StringType)):
        return str(python_type)
    
    type_name = python_type.__name__ if hasattr(python_type, '__name__') else str(python_type)
    
    if type_name in DTYPE_MAPPING:
        sql_type = DTYPE_MAPPING[type_name]
        return str(sql_type)
    
    return 'VARCHAR(255)'  # Default type


def get_string_type(max_length: int = 0) -> SqlType:
    """
    Get appropriate SQL string type based on the maximum string length.
    
    Args:
        max_length: Maximum string length, if greater than 255 returns Text type
    
    Returns:
        SqlType: SQL type object
    """
    if max_length > 255:
        return Text
    else:
        return String(max(max_length, 50))
