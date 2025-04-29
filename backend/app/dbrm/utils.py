"""
Data processing and SQL query generation utility functions.
"""
import logging
import json
import csv
import datetime
import os
from typing import Any, List, Dict

logger = logging.getLogger(__name__)


def format_value_for_sql(value: Any) -> str:
    """
    Format a value as a string representation for SQL statements based on its type.
    
    Args:
        value: The value to be formatted
    
    Returns:
        str: SQL formatted value
    """
    if value is None:
        return "NULL"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (list, dict)):
        # Serialize list or dict to JSON string
        return f"'{json.dumps(value, ensure_ascii=False)}'"
    elif isinstance(value, (datetime.date, datetime.datetime)):
        # Format date and time
        if isinstance(value, datetime.datetime):
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
        else:
            return f"'{value.strftime('%Y-%m-%d')}'"
    else:
        # String or other types, escape single quotes
        return f"'{str(value).replace('\'', '\'\'')}'"


def parse_sql_value(value: str, target_type: str) -> Any:
    """
    Convert SQL query result values to Python objects.
    
    Args:
        value: SQL returned value
        target_type: Target type name
        
    Returns:
        Converted Python object
    """
    if value is None:
        return None
    
    if target_type == 'json' or target_type == 'dict' or target_type == 'list':
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    elif target_type == 'datetime':
        try:
            return datetime.datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return value
    elif target_type == 'date':
        try:
            return datetime.date.fromisoformat(value)
        except (ValueError, TypeError):
            return value
    elif target_type == 'int':
        try:
            return int(value)
        except (ValueError, TypeError):
            return value
    elif target_type == 'float':
        try:
            return float(value)
        except (ValueError, TypeError):
            return value
    elif target_type == 'bool':
        if isinstance(value, (int, bool)):
            return bool(value)
        elif isinstance(value, str):
            return value.lower() in ('true', 'yes', 'y', '1')
        return bool(value)
    else:
        return value


def export_to_csv(data: List[Dict], filepath: str, encoding='utf-8') -> Dict[str, Any]:
    """
    Export data to a CSV file.
    
    Args:
        data: List of data to export (list of dictionaries)
        filepath: Output file path
        encoding: File encoding
        
    Returns:
        Dict: Result with success status, metadata and error message if any
    """
    if not data:
        return {
            'success': False,
            'error': "No data to export",
            'filepath': filepath
        }
    
    try:
        fieldnames = data[0].keys()
        with open(filepath, 'w', newline='', encoding=encoding) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return {
            'success': True,
            'filepath': filepath,
            'rows_exported': len(data),
            'columns': list(fieldnames)
        }
    except Exception as e:
        error_msg = f"Failed to export CSV: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'filepath': filepath
        }


def import_from_csv(filepath: str, encoding='utf-8') -> Dict[str, Any]:
    """
    Import data from a CSV file.
    
    Args:
        filepath: Input CSV file path
        encoding: File encoding
        
    Returns:
        Dict: Result containing success status, data, and error message if any
    """
    try:
        if not os.path.exists(filepath):
            error_msg = f"File does not exist: {filepath}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'filepath': filepath,
                'data': []
            }
            
        with open(filepath, 'r', newline='', encoding=encoding) as f:
            reader = csv.DictReader(f)
            data = list(reader)
            
            if not data:
                return {
                    'success': False,
                    'error': "CSV file is empty",
                    'filepath': filepath,
                    'data': []
                }
                
            return {
                'success': True,
                'filepath': filepath,
                'rows_imported': len(data),
                'columns': reader.fieldnames,
                'data': data
            }
    except Exception as e:
        error_msg = f"Failed to import CSV: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'filepath': filepath,
            'data': []
        }


def get_table_info(session, table_name: str) -> Dict:
    """
    Get table metadata information.
    
    Args:
        session: Database session
        table_name: Table name
        
    Returns:
        Dict: Table metadata information
    """
    try:
        # Execute different queries based on database type
        if session.engine.dialect == 'mysql':
            query = f"DESCRIBE {table_name}"
            result = session.execute(query).fetchall_as_dict()
            
            columns = []
            for row in result:
                columns.append({
                    'name': row['Field'],
                    'type': row['Type'],
                    'nullable': row['Null'] == 'YES',
                    'key': row['Key'],
                    'default': row['Default'],
                    'extra': row['Extra']
                })
                
            return {
                'table_name': table_name,
                'columns': columns
            }
        elif session.engine.dialect == 'mssql':
            query = f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
            result = session.execute(query).fetchall_as_dict()
            
            columns = []
            for row in result:
                columns.append({
                    'name': row['COLUMN_NAME'],
                    'type': row['DATA_TYPE'],
                    'nullable': row['IS_NULLABLE'] == 'YES',
                    'default': row['COLUMN_DEFAULT']
                })
                
            return {
                'table_name': table_name,
                'columns': columns
            }
        elif session.engine.dialect == 'sqlite':
            query = f"PRAGMA table_info('{table_name}')"
            result = session.execute(query).fetchall_as_dict()
            
            columns = []
            for row in result:
                columns.append({
                    'name': row['name'],
                    'type': row['type'],
                    'nullable': not row['notnull'],
                    'primary_key': bool(row['pk']),
                    'default': row['dflt_value']
                })
                
            return {
                'table_name': table_name,
                'columns': columns
            }
        else:
            logger.error(f"Unsupported database type: {session.engine.dialect}")
            return {'table_name': table_name, 'columns': []}
    except Exception as e:
        logger.error(f"Failed to get table information: {e}")
        return {'table_name': table_name, 'columns': []}