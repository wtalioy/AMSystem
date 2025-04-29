"""
DBRM utility decorators module.
"""
import logging
import functools
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

def db_operation_handler(operation_name: str = None):
    """
    Decorator: Provides unified error handling for database operation functions.
    
    Args:
        operation_name: Operation name for logging (if None, uses function name)
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            op_name = operation_name or func.__name__
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = f"{op_name} failed: {e}"
                logger.error(error_msg)
                return {'success': False, 'error': str(e)}
        return wrapper
    return decorator
