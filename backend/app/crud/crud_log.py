from typing import List

from app.dbrm import Session

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
        result = db.query(Log.duration).filter_by(
            worker_id=worker_id
        ).sum(Log.duration)
        return float(result) if result else 0.0
    
    def get_total_cost_by_order(self, db: Session, order_id: str) -> float:
        """Get total material cost for an order"""
        result = db.query(Log.cost).filter_by(
            order_id=order_id
        ).sum(Log.cost)
        return float(result) if result else 0.0


log = CRUDLog(Log)
