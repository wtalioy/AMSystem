from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app import crud
from app.schemas.car import CarCreate, CarUpdate
from app.models.car import Car

def create_car(db: Session, obj_in: CarCreate, customer_id: str) -> Car:
    """Register a new car for a customer"""
    return crud.car.create_car_with_owner(
        db=db, obj_in=obj_in, customer_id=customer_id
    )

def get_car_by_id(db: Session, car_id: str) -> Optional[Car]:
    """Get a specific car by ID"""
    return crud.car.get_by_car_id(db, car_id=car_id)

def get_customer_cars(db: Session, customer_id: str) -> List[Car]:
    """Get all cars owned by a customer"""
    return crud.car.get_cars_by_customer(db, customer_id=customer_id)

def update_car(db: Session, car_id: str, obj_in: CarUpdate) -> Optional[Car]:
    """Update car information"""
    car = crud.car.get_by_car_id(db, car_id=car_id)
    if not car:
        return None
    return crud.car.update(db, db_obj=car, obj_in=obj_in)

def get_cars_by_type(db: Session, car_type: int) -> List[Car]:
    """Get all cars of a specific type"""
    return crud.car.get_cars_by_type(db, car_type=car_type)

def get_all_cars(db: Session, skip: int = 0, limit: int = 100) -> List[Car]:
    """Get all cars (admin function)"""
    return crud.car.get_multi(db, skip=skip, limit=limit)

def get_car_maintenance_history(db: Session, car_id: str) -> List[Dict]:
    """Get maintenance history for a car"""
    orders = crud.order.get_orders_by_car(db, car_id=car_id)
    
    maintenance_history = []
    for order in orders:
        # Get all logs associated with this order
        logs = crud.log.get_logs_by_order(db, order_id=order.order_id)
        
        # Calculate costs
        material_cost = sum(log.cost for log in logs)
        labor_cost = 0
        
        # Collect maintenance details
        maintenance_entry = {
            "order_id": order.order_id,
            "start_date": order.start_time,
            "end_date": order.end_time,
            "description": order.description,
            "status": order.status,
            "material_cost": material_cost,
            "logs": logs
        }
        maintenance_history.append(maintenance_entry)
    
    return maintenance_history
