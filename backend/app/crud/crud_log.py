from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.crud.base import CRUDBase
from app.models.log import Log
from app.schemas.log import LogCreate, LogUpdate


class CRUDLog(CRUDBase[Log, LogCreate, LogUpdate]):
    def get_by_log_id(self, db: Session, log_id: str) -> Optional[Log]:
        return db.query(Log).filter(Log.id == log_id).first()
        
    def get_logs_by_order(
        self, db: Session, order_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        return db.query(Log).filter(
            Log.order_id == order_id
        ).order_by(desc(Log.log_time)).offset(skip).limit(limit).all()
        
    def get_logs_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        return db.query(Log).filter(
            Log.worker_id == worker_id
        ).order_by(desc(Log.log_time)).offset(skip).limit(limit).all()

    def create_log_for_order(
        self, db: Session, *, obj_in: LogCreate, worker_id: str
    ) -> Log:
        # Generate unique log ID
        from datetime import datetime
        import random
        import string
        now = datetime.now()
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        log_id = f"L{now.strftime('%y%m%d')}{random_suffix}"
        
        db_obj = Log(
            id=log_id,
            consumption=obj_in.consumption,
            cost=obj_in.cost,
            duration=obj_in.duration,
            order_id=obj_in.order_id,
            worker_id=worker_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_total_duration_by_worker(self, db: Session, worker_id: str) -> float:
        """Get total working hours for a worker"""
        result = db.query(func.sum(Log.duration)).filter(
            Log.worker_id == worker_id
        ).scalar()
        return float(result) if result else 0.0
    
    def get_total_cost_by_order(self, db: Session, order_id: str) -> float:
        """Get total material cost for an order"""
        result = db.query(func.sum(Log.cost)).filter(
            Log.order_id == order_id
        ).scalar()
        return float(result) if result else 0.0


log = CRUDLog(Log)
