from typing import List
from decimal import Decimal
from datetime import datetime

from app.dbrm import Session, func

from app.models import Log as LogModel
from app.schemas import LogCreate, Log


class CRUDLog:
    def get_logs_by_order(
        self, db: Session, order_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        objs = db.query(LogModel).filter_by(
            order_id=order_id
        ).order_by_desc(LogModel.log_time).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Log.model_validate(obj) for obj in objs]
    
    def get_logs_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        objs = db.query(LogModel).filter_by(
            worker_id=worker_id
        ).order_by_desc(LogModel.log_time).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Log.model_validate(obj) for obj in objs]
        
    def calculate_avg_cost_by_car_type(self, db: Session, car_type: int) -> float:
        from app.models import ServiceOrder, Car
        from app.dbrm import Condition
        
        cost_result = db.query(func.avg(LogModel.cost)).join(
            ServiceOrder, on=(ServiceOrder.order_id, LogModel.order_id)
        ).join(
            Car, on=(Car.car_id, ServiceOrder.car_id)
        ).filter(
            Condition.eq(Car.car_type, car_type)
        ).scalar()
        
        return float(cost_result) if cost_result else 0
    
    def calculate_avg_cost_by_car_type_period(self, db: Session, car_type: int, start_date: datetime, end_date: datetime) -> float:
        from app.models import ServiceOrder, Car
        from app.dbrm import Condition
        
        cost_result = db.query(func.avg(LogModel.cost)).join(
            ServiceOrder, on=(ServiceOrder.order_id, LogModel.order_id)
        ).join(
            Car, on=(Car.car_id, ServiceOrder.car_id)
        ).filter(
            Condition.eq(Car.car_type, car_type),
            Condition.gte(ServiceOrder.start_time, start_date),
            Condition.lte(ServiceOrder.start_time, end_date)
        ).scalar()
        
        return float(cost_result) if cost_result else 0
    
    def get_car_type_consumption(self, db: Session, car_type: int) -> List[tuple]:
        from app.models import ServiceOrder, Car
        from app.dbrm import Condition
        
        return db.query(LogModel.consumption).join(
            ServiceOrder, on=(ServiceOrder.order_id, LogModel.order_id)
        ).join(
            Car, on=(Car.car_id, ServiceOrder.car_id)
        ).filter(
            Condition.eq(Car.car_type, car_type)
        ).all()

    def calculate_total_hours_by_worker_type(self, db: Session, worker_type: int, start_time: str, end_time: str) -> float:
        from app.models import Worker
        from app.dbrm import Condition

        hours_result = db.query(func.sum(LogModel.duration)).join(
            Worker, on=(Worker.user_id, LogModel.worker_id)
        ).filter(
            Condition.eq(Worker.worker_type, worker_type),
            Condition.gte(LogModel.log_time, start_time),
            Condition.lte(LogModel.log_time, end_time)
        ).scalar()

        return float(hours_result) if hours_result else 0

    def create_log_for_order(
        self, db: Session, *, obj_in: LogCreate, worker_id: str
    ) -> Log:
        from datetime import datetime
        now = datetime.now()
        
        db_obj = LogModel(
            consumption=obj_in.consumption,
            cost=obj_in.cost,
            duration=obj_in.duration,
            order_id=obj_in.order_id,
            worker_id=worker_id,
            log_time=now,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return Log.model_validate(db_obj)
    
    def get_total_duration_by_worker(self, db: Session, worker_id: str) -> Decimal:
        result = db.query(func.sum(LogModel.duration)).filter_by(
            worker_id=worker_id
        ).scalar()
        return Decimal(result) if result else 0.0
    
    def get_total_cost_by_order(self, db: Session, order_id: str) -> Decimal:
        result = db.query(func.sum(LogModel.cost)).filter_by(
            order_id=order_id
        ).scalar()
        return Decimal(result) if result else 0.0
    
    def get_logs_by_order_and_worker(
        self, db: Session, order_id: str, worker_id: str
    ) -> List[Log]:
        """Get logs for a specific order and worker combination"""
        objs = db.query(LogModel).filter_by(
            order_id=order_id,
            worker_id=worker_id
        ).all()
        if not objs:
            return []
        return [Log.model_validate(obj) for obj in objs]


log = CRUDLog()
