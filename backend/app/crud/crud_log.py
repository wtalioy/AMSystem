from typing import List, Optional, Tuple, Dict, Any, Union

from app.dbrm import Session, func

from app.crud.base import CRUDBase
from app.models.log import Log
from app.schemas.log import LogCreate, LogUpdate


class CRUDLog(CRUDBase[Log, LogCreate, LogUpdate]):
    def get_logs_by_order(
        self, db: Session, order_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        return db.query(Log).filter_by(
            order_id=order_id
        ).order_by_desc(Log.log_time).offset(skip).limit(limit).all()
        
    def get_logs_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        return db.query(Log).filter_by(
            worker_id=worker_id
        ).order_by_desc(Log.log_time).offset(skip).limit(limit).all()
    
    def calculate_avg_cost_by_car_type(self, db: Session, car_type: int) -> float:
        from app.models.order import ServiceOrder
        from app.models.car import Car
        from app.dbrm import Condition
        
        cost_result = db.query(func.avg(Log.cost)).join(
            ServiceOrder, on=(ServiceOrder.order_id, Log.order_id)
        ).join(
            Car, on=(Car.car_id, ServiceOrder.car_id)
        ).where(
            Condition.eq(Car.car_type, car_type)
        ).scalar()
        
        return float(cost_result) if cost_result else 0

    def count_tasks_by_worker_type(self, db: Session, worker_type: int, start_time: str, end_time: str) -> int:
        from app.models.user import Worker
        from app.dbrm import Condition
        
        return db.query(func.count(Log.id)).join(
            Worker, on=(Worker.user_id, Log.worker_id)
        ).where(
            Condition.eq(Worker.worker_type, worker_type),
            Condition.ge(Log.log_time, start_time),
            Condition.le(Log.log_time, end_time)
        ).scalar() or 0

    def calculate_total_hours_by_worker_type(self, db: Session, worker_type: int, start_time: str, end_time: str) -> float:
        from app.models.user import Worker
        from app.dbrm import Condition

        hours_result = db.query(func.sum(Log.duration)).join(
            Worker, on=(Worker.user_id, Log.worker_id)
        ).where(
            Condition.eq(Worker.worker_type, worker_type),
            Condition.ge(Log.log_time, start_time),
            Condition.le(Log.log_time, end_time)
        ).scalar()

        return float(hours_result) if hours_result else 0

    def create_log_for_order(
        self, db: Session, *, obj_in: LogCreate, worker_id: str
    ) -> Log:
        from datetime import datetime
        now = datetime.now()
        
        db_obj = Log(
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
        
        return db_obj
    
    def get_total_duration_by_worker(self, db: Session, worker_id: str) -> float:
        """Get total working hours for a worker"""
        result = db.query(func.sum(Log.duration)).filter_by(
            worker_id=worker_id
        ).scalar()
        return float(result) if result else 0.0
    
    def get_total_cost_by_order(self, db: Session, order_id: str) -> float:
        """Get total material cost for an order"""
        result = db.query(func.sum(Log.cost)).filter_by(
            order_id=order_id
        ).scalar()
        return float(result) if result else 0.0


log = CRUDLog(Log)
