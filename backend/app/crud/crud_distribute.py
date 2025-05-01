from typing import List, Optional
from decimal import Decimal

from app.dbrm import Session

from app.crud.base import CRUDBase
from app.models.distribute import Distribute
from app.schemas.distribute import DistributeCreate, DistributeUpdate


class CRUDDistribute(CRUDBase[Distribute, DistributeCreate, DistributeUpdate]):
    def get_by_id(self, db: Session, distribute_id: int) -> Optional[Distribute]:
        return db.query(Distribute).filter_by(distribute_id=distribute_id).first()
    
    def get_distributions_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100
    ) -> List[Distribute]:
        return db.query(Distribute).filter_by(worker_id=worker_id).order_by_desc(Distribute.distribute_time).offset(skip).limit(limit).all()
    
    def create_distribution(
        self, db: Session, *, obj_in: DistributeCreate
    ) -> Distribute:
        db_obj = Distribute(
            amount=obj_in.amount,
            worker_id=obj_in.worker_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_total_payment_for_worker(self, db: Session, worker_id: str) -> Decimal:
        """Get total payment amount for a worker"""
        result = db.query(Distribute).filter_by(worker_id=worker_id).sum(Distribute.amount)
        return result if result else Decimal('0.0')


distribute = CRUDDistribute(Distribute)
