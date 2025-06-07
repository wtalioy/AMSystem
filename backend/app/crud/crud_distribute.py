from typing import List, Optional
from decimal import Decimal

from app.dbrm import Session, func

from app.models import Distribute as DistributeModel
from app.schemas import DistributeCreate, Distribute


class CRUDDistribute:
    def get_by_id(self, db: Session, distribute_id: int) -> Optional[Distribute]:
        obj = db.query(DistributeModel).filter_by(distribute_id=distribute_id).first()
        if not obj:
            return None
        return Distribute.model_validate(obj)
    
    def get_distributions_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100
    ) -> List[Distribute]:
        objs = db.query(DistributeModel).filter_by(worker_id=worker_id).order_by_desc(DistributeModel.distribute_time).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Distribute.model_validate(obj) for obj in objs]
    
    def create_distribution(
        self, db: Session, *, obj_in: DistributeCreate
    ) -> Distribute:
        db_obj = DistributeModel(
            amount=obj_in.amount,
            worker_id=obj_in.worker_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return Distribute.model_validate(db_obj)
    
    def get_total_payment_for_worker(self, db: Session, worker_id: str) -> Decimal:
        """Get total payment amount for a worker"""
        result = db.query(func.sum(DistributeModel.amount)).filter_by(worker_id=worker_id).scalar()
        return result if result else Decimal('0.0')
    
    def get_all_distributions(self, db: Session, skip: int = 0, limit: int = 100) -> List[Distribute]:
        objs = db.query(DistributeModel).order_by(DistributeModel.distribute_time).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Distribute.model_validate(obj) for obj in objs]


distribute = CRUDDistribute()
