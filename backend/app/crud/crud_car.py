from typing import List, Optional, Tuple

from app.dbrm import Session, func

from app.crud.base import CRUDBase
from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate


class CRUDCar(CRUDBase[Car, CarCreate, CarUpdate]):
    def get_by_car_id(self, db: Session, car_id: str) -> Optional[Car]:
        return db.query(Car).filter_by(car_id=car_id).first()
        
    def get_cars_by_customer(self, db: Session, customer_id: str) -> List[Car]:
        return db.query(Car).filter_by(customer_id=customer_id).all()
        
    def get_cars_by_type(self, db: Session, car_type: int) -> List[Car]:
        return db.query(Car).filter_by(car_type=car_type).all()
    
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
    
    def get_all_car_types(self, db: Session) -> List[Tuple[int]]:
        return db.query(func.distinct(Car.car_type)).all()

    def count_cars_by_type(self, db: Session, car_type: int) -> int:
        from app.dbrm import Condition
        return db.query(func.count(Car.car_id)).where(
            Condition.eq(Car.car_type, car_type)
        ).scalar() or 0


car = CRUDCar(Car)
