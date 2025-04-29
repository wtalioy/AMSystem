from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.dbrm.schema import TableBase
from app.dbrm.session import Session
from app.dbrm.query import Select, Insert, Update, Delete

ModelType = TypeVar("ModelType", bound=Any)  # Updated to allow any model type
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        * `model`: A model class (previously SQLAlchemy, now using custom dbrm)
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """通过ID获取单个对象"""
        # 使用模型的 get 类方法 (如果有)
        if hasattr(self.model, 'get'):
            return self.model.get(db, id)
            
        # 使用 query API
        return db.query(self.model).filter_by(**{self._get_primary_key_column(): id}).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """获取多个对象"""
        # 使用模型的 get_all 类方法 (如果有)
        if hasattr(self.model, 'get_all'):
            return self.model.get_all(db, limit=limit, offset=skip)
            
        # 使用 query API
        query = db.query(self.model).offset(skip).limit(limit)
        return query.all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """创建新对象"""
        obj_in_data = jsonable_encoder(obj_in)
        
        # 创建模型实例
        db_obj = self.model()
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
            
        # 保存到数据库
        if hasattr(db_obj, 'save'):
            db_obj.save(db)
        else:
            # 使用 Insert 构建器
            from app.dbrm.query import Insert
            query = Insert().into(self.model.__tablename__).columns_(*obj_in_data.keys()).values_(*obj_in_data.values())
            db.execute(query)
            db.commit()
            
            # 获取主键值并重新获取对象
            pk_column = self._get_primary_key_column()
            pk_value = obj_in_data.get(pk_column)
            return self.get(db, pk_value)
            
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """更新对象"""
        # 获取主键列和值
        pk_column = self._get_primary_key_column()
        pk_value = getattr(db_obj, pk_column)
        
        # 准备更新数据
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 更新实例属性
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        # 保存到数据库
        if hasattr(db_obj, 'save'):
            db_obj.save(db)
        else:
            # 使用 Update 构建器
            from app.dbrm.query import Update, Condition
            query = Update().table_(self.model.__tablename__).set_(**update_data).where(
                Condition.eq(pk_column, pk_value)
            )
            db.execute(query)
            db.commit()
            
            # 重新获取更新后的对象
            return self.get(db, pk_value)
            
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType:
        """删除对象"""
        # 先获取对象
        obj = self.get(db, id)
        if not obj:
            return None
            
        # 使用 delete 方法（如果有）
        if hasattr(obj, 'delete'):
            obj.delete(db)
        else:
            # 获取主键列
            pk_column = self._get_primary_key_column()
            
            # 使用 Delete 构建器
            from app.dbrm.query import Delete, Condition
            query = Delete().from_(self.model.__tablename__).where(
                Condition.eq(pk_column, id)
            )
            
            db.execute(query)
            db.commit()
            
        return obj
        
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name from the model"""
        # Check if the model has defined primary key columns
        if hasattr(self.model, '_columns'):
            for name, column in self.model._columns.items():
                if hasattr(column, 'primary_key') and column.primary_key:
                    return name
        
        # Default to 'id' if no primary key is explicitly defined
        return 'id'
        
    def _row_to_model(self, row) -> ModelType:
        """Convert a database row to a model instance"""
        if isinstance(row, tuple):
            # If row is a tuple, convert to dict using column names
            # This assumes columns are returned in the same order as defined in the model
            column_names = list(self.model._columns.keys()) if hasattr(self.model, '_columns') else []
            row_data = dict(zip(column_names, row))
        else:
            row_data = row
            
        return self.model(**row_data)
