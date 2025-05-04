"""
DBRM utility decorators module.
"""
import logging
import functools
from typing import Callable, Dict, Any, Type, List, Optional, Set, TypeVar, cast

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

# Global registry for storing all registered model classes
_MODEL_REGISTRY: Dict[str, Type] = {}
# Store dependencies between models
_MODEL_DEPENDENCIES: Dict[str, Set[str]] = {}
# Store model priorities
_MODEL_PRIORITIES: Dict[str, int] = {}

T = TypeVar('T')

def model_register(cls_or_priority=None, *, dependencies: Optional[List[str]] = None, priority: int = 100):
    """
    Decorator for registering model classes.
    Can be used as a simple decorator: @model_register
    Or with parameters: @model_register(priority=10, dependencies=["User"])
    
    Args:
        cls_or_priority: Can be the decorated class or a priority value
        dependencies: List of other models this model depends on
        priority: Model priority, smaller number means higher priority, default is 100
        
    Returns:
        Decorated class
    """
    # Handle no-parameter call: @model_register
    if isinstance(cls_or_priority, type):
        return _register_model(cls_or_priority, dependencies or [], priority)
    
    # Handle parameterized call: @model_register(priority=10, dependencies=["User"])
    actual_priority = cls_or_priority if isinstance(cls_or_priority, int) else priority
    
    def decorator(cls: Type[T]) -> Type[T]:
        return _register_model(cls, dependencies or [], actual_priority)
    
    return decorator

def _register_model(cls: Type[T], dependencies: List[str], priority: int) -> Type[T]:
    """Internal function: Actual logic for model registration"""
    model_name = cls.__name__
    if model_name in _MODEL_REGISTRY:
        logger.warning(f"Model {model_name} already registered, overwriting.")
    
    _MODEL_REGISTRY[model_name] = cls
    _MODEL_DEPENDENCIES[model_name] = set(dependencies)
    _MODEL_PRIORITIES[model_name] = priority
    
    logger.debug(f"Registered model: {model_name} with priority {priority}")
    
    return cls

def get_registered_models() -> Dict[str, Type]:
    """
    Get all registered model classes
    
    Returns:
        Dict[str, Type]: A dictionary mapping model names to model classes
    """
    return _MODEL_REGISTRY.copy()

def _resolve_dependencies() -> List[str]:
    """
    Resolve model dependencies, return a list of model names sorted by dependency order
    
    Returns:
        List[str]: List of model names sorted by dependency order
    """
    # Topological sort
    result = []
    visited = set()
    temp_mark = set()

    def visit(node):
        if node in temp_mark:
            raise ValueError(f"Circular dependency detected: {node}")
        if node not in visited:
            temp_mark.add(node)
            
            # Recursively visit dependencies
            for dep in _MODEL_DEPENDENCIES.get(node, set()):
                if dep not in _MODEL_REGISTRY:
                    logger.warning(f"Model {node} depends on {dep}, but {dep} is not registered.")
                    continue
                visit(dep)
            
            temp_mark.remove(node)
            visited.add(node)
            result.append(node)

    sorted_models = sorted(_MODEL_REGISTRY.keys(), 
                         key=lambda model: _MODEL_PRIORITIES.get(model, 100))
    
    # Execute topological sort starting from each model
    for model in sorted_models:
        if model not in visited:
            visit(model)
    
    return result

def create_all_tables(session) -> List[str]:
    """
    Create all registered model tables
    
    Args:
        session: Database session object
        
    Returns:
        List[str]: List of successfully created table names
    """
    created_tables = []
    
    sorted_models = _resolve_dependencies()
    
    # Create tables in order
    for model_name in sorted_models:
        try:
            model_class = _MODEL_REGISTRY[model_name]
            model_class.create(session)
            created_tables.append(model_class.__tablename__)
            logger.info(f"Created table: {model_class.__tablename__}")
        except Exception as e:
            logger.error(f"Failed to create table {model_name}: {e}")
    
    return created_tables

def drop_all_tables(session) -> List[str]:
    """
    Drop all registered model tables
    
    Args:
        session: Database session object
        
    Returns:
        List[str]: List of successfully dropped table names
    """
    dropped_tables = []
    
    sorted_models = _resolve_dependencies()
    
    for model_name in reversed(sorted_models):
        try:
            model_class = _MODEL_REGISTRY[model_name]
            model_class.drop(session)
            dropped_tables.append(model_class.__tablename__)
            logger.info(f"Dropped table: {model_class.__tablename__}")
        except Exception as e:
            logger.error(f"Failed to drop table {model_name}: {e}")
    
    return dropped_tables
