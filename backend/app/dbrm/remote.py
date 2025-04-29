import logging
from typing import List, Dict, Any
from .session import Session
from .utils import format_value_for_sql, export_to_csv, import_from_csv
from .types import get_sql_type, get_string_type
from .decorators import db_operation_handler

logger = logging.getLogger(__name__)

def infer_schema_from_dict_list(data: List[Dict], table_name: str) -> str:
    if not data:
        raise ValueError("Data list is empty, unable to infer schema")
    
    # Get all column names
    columns = []
    sample_row = data[0]
    
    # Analyze the data type of each column
    for col_name, value in sample_row.items():
        if isinstance(value, str):
            str_values = [str(row.get(col_name, "")) for row in data if row.get(col_name) is not None]
            max_length = max([len(v) for v in str_values]) if str_values else 0
            sql_type = get_string_type(max_length)
        else:
            sql_type = get_sql_type(type(value) if value is not None else str)
            
        columns.append(f"{col_name} {sql_type}")
    
    create_query = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n)"
    return create_query


def _insert_data_to_table(data: List[Dict], table_name: str, session: Session) -> int:
    """
    Insert data into an existing table.
    
    Args:
        data: List of dictionaries
        table_name: Table name
        session: Database session
        
    Returns:
        int: Number of inserted rows
    """
    if not data:
        return 0
        
    columns = list(data[0].keys())
    columns_str = ', '.join(columns)
    
    batch_size = 1000
    total_rows = 0
    
    for i in range(0, len(data), batch_size):
        batch_data = data[i:i+batch_size]
        values_list = []
        
        for row in batch_data:
            values = []
            for col in columns:
                val = row.get(col)
                values.append(format_value_for_sql(val))
            values_list.append(f"({', '.join(values)})")
        
        if values_list:
            values_str = ', '.join(values_list)
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES {values_str}"
            try:
                session.execute(insert_query)
                total_rows += len(batch_data)
            except Exception as e:
                logger.error(f"Failed to insert data: {e}")
                raise
    
    return total_rows


@db_operation_handler("CSV Transfer")
def transfer_csv(csv_path: str, table_name: str, session: Session, 
                 if_exists: str = 'replace', index: bool = False, 
                 encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    Transfer a CSV file to a database table.
    
    Args:
        csv_path: CSV file path
        table_name: Target table name
        session: Database session
        if_exists: Behavior if table exists ('replace', 'append', 'fail')
        index: Whether to include index (not used in current implementation)
        encoding: CSV file encoding
        
    Returns:
        Dict: Dictionary containing operation results
    """
    # Read data from CSV file
    import_result = import_from_csv(csv_path, encoding=encoding)
    
    # Return error if import failed
    if not import_result['success']:
        import_result['csv_path'] = csv_path  # For consistency
        return import_result
    
    # Use import_data function to import data to database
    result = import_data(import_result['data'], table_name, session, if_exists)
    
    # Add CSV file information to the result
    if result['success']:
        result['csv_path'] = csv_path
        result['rows_imported'] = import_result.get('rows_imported', 0)
        result['columns_imported'] = import_result.get('columns', [])
    
    return result


@db_operation_handler("Export Query to CSV")
def export_query_to_csv(query: str, output_path: str, session: Session, 
                       encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    Export query results to a CSV file.
    
    Args:
        query: SQL query
        output_path: Output CSV file path
        session: Database session
        encoding: CSV file encoding
        
    Returns:
        Dict: Dictionary containing operation results
    """
    # Execute the query
    session.execute(query)
    results = session.fetchall_as_dict()
    
    # Handle empty results case
    if not results:
        return {
            'success': False, 
            'error': "Query returned no results", 
            'output_path': output_path,
            'query': query
        }
    
    # Use the enhanced export_to_csv function which now returns a dictionary
    export_result = export_to_csv(results, output_path, encoding)
    
    # Rename 'filepath' to 'output_path' for consistency with the API
    if 'filepath' in export_result:
        export_result['output_path'] = export_result.pop('filepath')
    
    # Add query information to the result
    export_result['query'] = query
    
    return export_result


@db_operation_handler("Data Import")
def import_data(data: List[Dict], table_name: str, session: Session,
              if_exists: str = 'append') -> Dict[str, Any]:
    """
    Import data into a database table.
    
    Args:
        data: Data list (list of dictionaries)
        table_name: Target table name
        session: Database session
        if_exists: Behavior if table exists ('replace', 'append', 'fail')
        
    Returns:
        Dict: Dictionary containing operation results
    """
    if not data:
        return {'success': False, 'error': "No data to import"}
        
    # Check if table exists
    try:
        session.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        table_exists = True
    except Exception:
        table_exists = False
        
    # Handle existing table
    if table_exists:
        if if_exists == 'fail':
            return {'success': False, 'error': f"Table already exists: {table_name}"}
        elif if_exists == 'replace':
            session.execute(f"DROP TABLE {table_name}")
            table_exists = False
            
    # Create table (if needed)
    if not table_exists:
        create_query = infer_schema_from_dict_list(data, table_name)
        session.execute(create_query)
        
    # Insert data
    rows_inserted = _insert_data_to_table(data, table_name, session)
    session.commit()
    
    return {
        'success': True,
        'table_name': table_name,
        'rows_inserted': rows_inserted,
        'columns': list(data[0].keys()) if data else []
    }
