from typing import List, Optional, Tuple, Dict, Any

from app.dbrm import Session, func

from app.models import Car as CarModel
from app.schemas import CarCreate, Car, CarUpdate


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
        
    def get_cars_by_type(self, db: Session, car_type: int, skip: int = 0, limit: int = 100) -> List[Car]:
        objs = db.query(CarModel).filter_by(car_type=car_type).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Car.model_validate(obj) for obj in objs]
    
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
    
    def get_all_car_types(self, db: Session) -> List[Tuple[int]]:
        return db.query(func.distinct(CarModel.car_type)).all()

    def count_cars_by_type(self, db: Session, car_type: int) -> int:
        return db.query(func.count(CarModel.car_id)).filter_by(
            car_type=car_type
        ).scalar() or 0


car = CRUDCar()
