from typing import List, Optional

from app.dbrm.session import Session

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


car = CRUDCar(Car)
