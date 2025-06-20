from typing import Optional, List, Dict, Any
from app.dbrm import Session

from app.crud import car, order, log
from app.schemas import CarCreate, CarUpdate, Car, CarType
from app.core.audit_decorators import audit


class CarService:
    """Service for car operations"""

    @staticmethod
    def get_valid_car_types(db: Session) -> List[str]:
        """Get all car types"""
        return car.get_all_car_types(db)
    

    @staticmethod
    @audit("CarType", "CREATE")
    def create_car_type(db: Session, obj_in: CarType, audit_context=None) -> CarType:
        """Create a new car type"""
        car_types = car.get_all_car_types(db)
        if obj_in.car_type in car_types:
            raise ValueError(f"Car type already exists: {obj_in.car_type}")
        return car.create_car_type(db, obj_in=obj_in)
    

    @staticmethod
    @audit("Car", "CREATE")
    def create_car(db: Session, obj_in: CarCreate, customer_id: str, audit_context=None) -> Car:
        """Register a new car for a customer"""
        car_types = car.get_all_car_types(db)
        if obj_in.car_type not in car_types:
            raise ValueError(f"Unsupported car type: {obj_in.car_type}")
        return car.create_car_with_owner(
            db=db, obj_in=obj_in, customer_id=customer_id
        )


    @staticmethod
    def get_car_by_id(db: Session, car_id: str) -> Optional[Car]:
        """Get a specific car by ID"""
        car_obj = car.get_by_car_id(db, car_id=car_id)
        if car_obj:
            return car_obj
        return None


    @staticmethod
    def get_customer_cars(db: Session, customer_id: str, skip: int = 0, limit: int = 100) -> List[Car]:
        """Get all cars owned by a customer with pagination"""
        cars = car.get_cars_by_customer(db, customer_id=customer_id, skip=skip, limit=limit)
        return cars


    @staticmethod
    @audit("Car", "UPDATE")
    def update_car(db: Session, car_id: str, obj_in: CarUpdate, audit_context=None) -> Optional[Car]:
        """Update car information (full update)"""
        car_obj = car.get_by_car_id(db, car_id=car_id)
        if not car_obj:
            return None
        return car.update(db, obj_old=car_obj, obj_in=obj_in)


    @staticmethod
    @audit("Car", "UPDATE")
    def partial_update_car(db: Session, car_id: str, obj_in: Dict[str, Any], audit_context=None) -> Optional[Car]:
        """
        Partially update car information
        
        Only updates the fields that are provided in the input dictionary
        """
        car_obj = car.get_by_car_id(db, car_id=car_id)
        if not car_obj:
            return None
        
        # Convert dict to CarUpdate while preserving existing values
        car_data = car_obj.dict()
        for field in obj_in:
            if field in car_data:
                car_data[field] = obj_in[field]
        
        update_data = CarUpdate(**car_data)
        return car.update(db, db_obj=car_obj, obj_in=update_data)


    @staticmethod
    @audit("Car", "DELETE")
    def delete_car(db: Session, car_id: str, audit_context=None) -> bool:
        """
        Delete a car from the database
        
        Returns True if car was deleted, False if car was not found
        """
        car_obj = car.get_by_car_id(db, car_id=car_id)
        if not car_obj:
            return False
        
        car.remove(db, car_id=car_id)
        return True


    @staticmethod
    def get_cars_by_type(db: Session, car_type: str) -> List[Car]:
        """Get all cars of a specific type"""
        cars = car.get_cars_by_type(db, car_type=car_type)
        return cars


    @staticmethod
    def get_all_cars(db: Session, skip: int = 0, limit: int = 100) -> List[Car]:
        """Get all cars (admin function)"""
        cars = car.get_multi(db, skip=skip, limit=limit)
        return cars


    @staticmethod
    def get_car_maintenance_history(db: Session, car_id: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Get maintenance history for a car with pagination
        
        Returns a list of maintenance entries with order details and associated logs
        """
        orders = order.get_orders_by_car(db, car_id=car_id, skip=skip, limit=limit)
        
        maintenance_history = []
        for order_obj in orders:
            # Get all logs associated with this order
            logs = log.get_logs_by_order(db, order_id=order_obj.order_id)
            
            # Calculate costs
            material_cost = sum(log.cost for log in logs)
            
            # Collect maintenance details
            maintenance_entry = {
                "order_id": order_obj.order_id,
                "start_date": order_obj.start_time,
                "end_date": order_obj.end_time,
                "description": order_obj.description,
                "status": order_obj.status,
                "material_cost": material_cost,
                "logs": logs
            }
            maintenance_history.append(maintenance_entry)
        
        return maintenance_history
