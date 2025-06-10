from typing import List, Optional

from app.dbrm import Session, func

from app.models import Car as CarModel, CarType as CarTypeModel
from app.schemas import CarCreate, Car, CarUpdate, CarType


class CRUDCar:
    def get_by_car_id(self, db: Session, car_id: str) -> Optional[Car]:
        obj = db.query(CarModel).filter_by(car_id=car_id).first()
        if not obj:
            return None
        return Car.model_validate(obj)

    def get_cars_by_customer(self, db: Session, customer_id: str, skip: int = 0, limit: int = 100) -> List[Car]:
        objs = db.query(CarModel).filter_by(customer_id=customer_id).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Car.model_validate(obj) for obj in objs]
        
    def get_cars_by_type(self, db: Session, car_type: str, skip: int = 0, limit: int = 100) -> List[Car]:
        objs = db.query(CarModel).filter_by(car_type=car_type).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Car.model_validate(obj) for obj in objs]
    
    def create_car_type(self, db: Session, obj_in: CarType) -> CarType:
        db_obj = CarTypeModel(car_type=obj_in.car_type)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return CarType.model_validate(db_obj)
    
    def create_car_with_owner(
        self, db: Session, *, obj_in: CarCreate, customer_id: str
    ) -> Car:
        car = CarModel(
            car_id=obj_in.car_id,
            customer_id=customer_id,
            car_type=obj_in.car_type
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        return Car.model_validate(car)
    
    def update(
        self, db: Session, *, obj_old: Car, obj_in: CarUpdate
    ) -> Car:
        """
        Update a car
        """
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            if hasattr(obj_old, field):
                setattr(obj_old, field, value)
        
        db_obj = CarModel(
            car_id=obj_old.car_id,
            customer_id=obj_old.customer_id,
            car_type=obj_old.car_type
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(obj_old)
        return Car.model_validate(db_obj)
    
    def get_all_car_types(self, db: Session) -> List[str]:
        objs = db.query(CarTypeModel).all()
        if not objs:
            return []
        return [obj.car_type for obj in objs]

    def count_cars_by_type(self, db: Session, car_type: str) -> int:
        return db.query(func.count(CarModel.car_id)).filter_by(
            car_type=car_type
        ).scalar() or 0


car = CRUDCar()
