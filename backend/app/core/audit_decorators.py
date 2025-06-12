from typing import Optional, Dict, Any, Callable
from functools import wraps
from app.dbrm import Session
from app.schemas.audit_log import ChangeTrackingContext


class AuditConfig:
    """Convention-based audit configuration"""
    
    # Common ID field patterns by entity type
    ID_PATTERNS = {
        "Order": "order_id",
        "User": "user_id", 
        "Customer": "user_id",
        "Worker": "user_id", 
        "Administrator": "user_id",
        "Car": "car_id",
        "Procedure": "procedure_id",
        "Log": "log_id",
        "Wage": "worker_type"
    }
    
    @classmethod
    def get_id_field(cls, table_name: str) -> str:
        """Get the primary ID field for a table using conventions"""
        # Try exact match first
        if table_name in cls.ID_PATTERNS:
            return cls.ID_PATTERNS[table_name]
        
        # Try without 'Service' prefix
        clean_name = table_name.replace("Service", "")
        if clean_name in cls.ID_PATTERNS:
            return cls.ID_PATTERNS[clean_name]
        
        # Default convention: table_name_id (lowercase)
        return f"{table_name.lower()}_id"
    
    @classmethod
    def get_search_fields(cls, table_name: str) -> list:
        """Get fields to search for in function parameters"""
        id_field = cls.get_id_field(table_name)
        return [id_field, "id"]


class SimpleIdExtractor:
    """Simplified ID extraction with unified approach"""
    
    @staticmethod
    def extract_id(table_name: str, *args, **kwargs) -> Optional[str]:
        """Unified ID extraction using multiple strategies"""
        search_fields = AuditConfig.get_search_fields(table_name)
        
        # Strategy 1: Check kwargs first (most explicit)
        for field in search_fields:
            if field in kwargs and kwargs[field] is not None:
                return str(kwargs[field])
        
        # Strategy 2: Check positional args (db session at index 0)
        if len(args) >= 2:
            return str(args[1])  # Second argument is usually the ID
        
        return None
    
    @staticmethod
    def extract_from_result(result: Any, table_name: str) -> Optional[str]:
        """Extract ID from function result"""
        if not result:
            return None
        
        search_fields = AuditConfig.get_search_fields(table_name)
        
        # Try Pydantic model first
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            for field in search_fields:
                if field in result_dict and result_dict[field] is not None:
                    return str(result_dict[field])
        
        # Try direct attribute access
        for field in search_fields:
            if hasattr(result, field):
                value = getattr(result, field)
                if value is not None:
                    return str(value)
        
        return None


def audit(table_name: str, operation: str):
    """
    Simplified audit decorator
    
    Args:
        table_name: Name of the table being audited
        operation: Operation type (CREATE, UPDATE, DELETE)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _execute_with_audit(func, table_name, operation, *args, **kwargs)
        return wrapper
    return decorator


def _execute_with_audit(func: Callable, table_name: str, operation: str, *args, **kwargs):
    """Core audit execution logic - separated for clarity"""
    # Validate session
    db = args[0] if args else kwargs.get('db')
    if not isinstance(db, Session):
        raise ValueError("db is not a valid session")
    
    # Extract context
    context = kwargs.get('audit_context') or kwargs.get('context')
    
    # Pre-execution: Get old data for updates
    old_data = None
    if operation == "UPDATE":
        record_id = SimpleIdExtractor.extract_id(table_name, *args, **kwargs)
        if record_id:
            old_data = _get_old_data(db, table_name, record_id)
    
    # Execute the original function
    result = func(*args, **kwargs)
    
    # Post-execution: Log the change
    try:
        _args = args[1:]    
        _kwargs = kwargs.copy()
        _kwargs.pop('db', None)
        _log_audit_change(db, table_name, operation, old_data, result, context, *_args, **_kwargs)
    except Exception as e:
        # Don't fail the business operation if audit fails
        print(f"Audit logging failed: {e}")
    
    return result


def _get_old_data(db: Session, table_name: str, record_id: str) -> Optional[Dict]:
    """Get old data for update operations"""
    try:
        from app.services.audit_service import AuditService
        old_obj = AuditService._get_record_for_audit(db, table_name, record_id)
        if old_obj:
            return AuditService.serialize_for_audit(old_obj)
    except Exception:
        pass  # If we can't get old data, proceed without it
    return None


def _log_audit_change(db: Session, table_name: str, operation: str, old_data: Optional[Dict], 
                     result: Any, context: Optional[ChangeTrackingContext], *args, **kwargs):
    """Log the audit change"""
    from app.services.audit_service import AuditService
    
    # Extract record ID
    record_id = (
        SimpleIdExtractor.extract_from_result(result, table_name) or
        SimpleIdExtractor.extract_id(table_name, *args, **kwargs)
    )
    
    if not record_id:
        return  # Can't audit without a record ID
    
    # Prepare new data
    new_data = None
    if operation in ["CREATE", "UPDATE"] and result:
        new_data = AuditService.serialize_for_audit(result)
    
    # Log the change
    AuditService.log_change(
        db=db,
        table_name=table_name,
        record_id=record_id,
        operation=operation,
        old_data=old_data,
        new_data=new_data,
        context=context
    )