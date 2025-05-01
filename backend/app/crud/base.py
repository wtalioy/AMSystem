from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.dbrm.session import Session

ModelType = TypeVar("ModelType", bound=Any)  # Updated to allow any model type
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        """
        self.model = model    
        
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        if hasattr(self.model, 'get'):
            return self.model.get(db, id)
        else:
            raise AttributeError(f"Model class {self.model.__name__} must implement 'get' class method")    
        
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        if hasattr(self.model, 'get_all'):
            return self.model.get_all(db, limit=limit, offset=skip)
        else:
            raise AttributeError(f"Model class {self.model.__name__} must implement 'get_all' class method")

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new object"""
        obj_in_data = jsonable_encoder(obj_in)
        
        db_obj = self.model()
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
            
        if hasattr(db_obj, 'save'):
            db_obj.save(db)
        else:
            raise AttributeError(f"Model class {self.model.__name__} must implement 'save' class method")
            
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an object"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Update instance attributes
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        if hasattr(db_obj, 'save'):
            db_obj.save(db)
        else:
            raise AttributeError(f"Model class {self.model.__name__} must implement 'save' class method")
            
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType:
        """Delete an object"""
        obj = self.get(db, id)
        if not obj:
            return None
        if hasattr(obj, 'delete'):
            obj.delete(db)
        else:
            raise AttributeError(f"Model class {self.model.__name__} must implement 'delete' class method")
            
        return obj
        
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name of the model"""
        if hasattr(self.model, '_get_primary_key_info'):
            return self.model._get_primary_key_info()
            
        # Compatibility handling: check if the model defines a primary key column
        if hasattr(self.model, '_columns'):
            for name, column in self.model._columns.items():
                if hasattr(column, 'primary_key') and column.primary_key:
                    return name
        
        # If no primary key is explicitly defined, default to 'id'
        return 'id'
