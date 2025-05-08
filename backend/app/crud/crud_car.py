from typing import List, Optional, Tuple, Dict, Any

from app.dbrm import Session, func

from app.crud.base import CRUDBase
from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate


class CRUDCar(CRUDBase[Car, CarCreate, CarUpdate]):
    def get_by_car_id(self, db: Session, car_id: str) -> Optional[Car]:
        return db.query(Car).filter_by(car_id=car_id).first()
        
    def get_cars_by_customer(self, db: Session, customer_id: str, skip: int = 0, limit: int = 100) -> List[Car]:
        return db.query(Car).filter_by(customer_id=customer_id).offset(skip).limit(limit).all()
        
    def get_cars_by_type(self, db: Session, car_type: int, skip: int = 0, limit: int = 100) -> List[Car]:
        return db.query(Car).filter_by(car_type=car_type).offset(skip).limit(limit).all()
    
    def create_car_with_owner(
        self, db: Session, *, obj_in: CarCreate, customer_id: str
    ) -> Car:
        car = Car(
            car_id=obj_in.car_id,
            customer_id=customer_id,
            car_type=obj_in.car_type
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        return car
    
    def partial_update(
        self, db: Session, *, db_obj: Car, obj_in: Dict[str, Any]
    ) -> Car:
        """
        Partially update a car
        
        Only updates fields provided in the input dictionary
        """
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_all_car_types(self, db: Session) -> List[Tuple[int]]:
        return db.query(func.distinct(Car.car_type)).all()

    def count_cars_by_type(self, db: Session, car_type: int) -> int:
        from app.dbrm import Condition
        return db.query(func.count(Car.car_id)).where(
            Condition.eq(Car.car_type, car_type)
        ).scalar() or 0


car = CRUDCar(Car)
