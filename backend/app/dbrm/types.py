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


class CharType(SqlType):
    """CHAR type, supports specifying length"""
    def __init__(self, length=1):
        self.length = length
        super().__init__(f"CHAR({length})")
    
    def __call__(self, length):
        """Supports usage like Char(10)"""
        return CharType(length)


class NumericType(SqlType):
    """NUMERIC type, supports specifying precision and scale"""
    def __init__(self, precision=10, scale=2):
        self.precision = precision
        self.scale = scale
        super().__init__(f"NUMERIC({precision},{scale})")
    
    def __call__(self, precision, scale=2):
        """Supports usage like Numeric(15,4)"""
        return NumericType(precision, scale)


class DecimalType(SqlType):
    """DECIMAL type, supports specifying precision and scale"""
    def __init__(self, precision=10, scale=2):
        self.precision = precision
        self.scale = scale
        super().__init__(f"DECIMAL({precision},{scale})")
    
    def __call__(self, precision, scale=2):
        """Supports usage like Decimal(15,4)"""
        return DecimalType(precision, scale)


Integer = SqlType('INTEGER')
Float = SqlType('FLOAT')
Double = SqlType('DOUBLE')
Boolean = SqlType('BOOLEAN')
String = StringType()
Char = CharType()
VarChar = StringType() # same with String
Text = SqlType('TEXT')
DateTime = SqlType('DATETIME')
Date = SqlType('DATE')
Time = SqlType('TIME')
Timestamp = SqlType('TIMESTAMP')
JSON = SqlType('TEXT')
BLOB = SqlType('BLOB')
TinyText = SqlType('TINYTEXT')
LongText = SqlType('LONGTEXT')
TinyInt = SqlType('TINYINT')
SmallInt = SqlType('SMALLINT')
BigInt = SqlType('BIGINT')
Decimal = DecimalType()
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
    'char': Char,
    'varchar': VarChar,
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
    if isinstance(python_type, (SqlType, StringType, CharType, NumericType, DecimalType)):
        return str(python_type)
    
    type_name = python_type.__name__ if hasattr(python_type, '__name__') else str(python_type)
    
    if type_name in DTYPE_MAPPING:
        sql_type = DTYPE_MAPPING[type_name]
        return str(sql_type)
    
    return 'VARCHAR(255)'  # Default type


def get_string_type(max_length: int = 0, fixed_length: bool = False) -> SqlType:
    """
    Get appropriate SQL string type based on the maximum string length.
    
    Args:
        max_length: Maximum string length, if greater than 255 returns Text type
        fixed_length: If True, returns Char type, otherwise returns VarChar
    
    Returns:
        SqlType: SQL type object
    """
    if max_length > 255:
        return Text
    else:
        if fixed_length:
            return Char(max(max_length, 1))
        else:
            return VarChar(max(max_length, 50))
