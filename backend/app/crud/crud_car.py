from typing import List, Optional, Dict, Any

from app.crud.base import CRUDBase
from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate
from app.dbrm.session import Session
from app.dbrm.query import Select, Insert, Condition


class CRUDCar(CRUDBase[Car, CarCreate, CarUpdate]):
    def get_by_car_id(self, db: Session, car_id: str) -> Optional[Car]:
        query = db.query(self.model).filter_by(car_id=car_id).first()
        return query
        
    def get_cars_by_customer(self, db: Session, customer_id: str) -> List[Car]:
        """获取客户的所有车辆"""
        query = Select().from_(self.model).where(
            Condition.eq("customer_id", customer_id)
        )
        
        # 执行查询并返回结果
        db.execute(query)
        cars_data = db.fetchall_as_dict()
        return [self.model._from_row(car_data) for car_data in cars_data]
        
    def get_cars_by_type(self, db: Session, car_type: int) -> List[Car]:
        """获取指定类型的所有车辆"""
        # 使用链式 API
        return db.query(self.model).filter_by(car_type=car_type).all()
    
    def create_car_with_owner(
        self, db: Session, *, obj_in: CarCreate, customer_id: str
    ) -> Car:
        """创建带有所有者的车辆"""
        obj_in_data = obj_in.model_dump()
        obj_in_data["customer_id"] = customer_id
        
        # 创建新的车辆实例
        car = Car()
        for key, value in obj_in_data.items():
            setattr(car, key, value)
        
        # 保存到数据库
        car.save(db)
        
        return car


car = CRUDCar(Car)
