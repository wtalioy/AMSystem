from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate


class CRUDCar(CRUDBase[Car, CarCreate, CarUpdate]):
    def get_by_car_id(self, db: Session, car_id: str) -> Optional[Car]:
        return db.query(Car).filter(Car.car_id == car_id).first()
        
    def get_cars_by_customer(self, db: Session, customer_id: str) -> List[Car]:
        return db.query(Car).filter(Car.customer_id == customer_id).all()
        
    def get_cars_by_type(self, db: Session, car_type: int) -> List[Car]:
        return db.query(Car).filter(Car.car_type == car_type).all()
    
    def create_car_with_owner(
        self, db: Session, *, obj_in: CarCreate, customer_id: str
    ) -> Car:
        obj_in_data = obj_in.dict()
        obj_in_data["customer_id"] = customer_id
        db_obj = Car(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


car = CRUDCar(Car)
