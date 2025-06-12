from typing import List, Optional
from decimal import Decimal
from datetime import datetime

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
        from datetime import datetime
        
        db_obj = DistributeModel(
            amount=obj_in.amount,
            worker_id=obj_in.worker_id,
            distribute_time=datetime.now()
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

    def get_labor_cost_breakdown_by_period(self, db: Session, start_date: datetime, end_date: datetime, period_type: str = "month") -> dict:
        """Get labor cost breakdown by period from distribute payments"""
        from app.dbrm import Condition, func
        
        if period_type == "quarter":
            date_part = func.concat(
                func.extract('year', DistributeModel.distribute_time), 
                '-Q', 
                func.ceil(func.arithmetic(func.extract('month', DistributeModel.distribute_time), '/', 3))
            )
        else:
            date_part = func.date_format(DistributeModel.distribute_time, '%Y-%m')
        
        labor_query = db.query(date_part, func.sum(DistributeModel.amount)).where(
            Condition.gte(DistributeModel.distribute_time, start_date),
            Condition.lte(DistributeModel.distribute_time, end_date)
        ).group_by(date_part)
        
        labor_results = labor_query.all()
        
        breakdown = {}
        for period, labor_cost in labor_results:
            breakdown[period] = float(labor_cost) if labor_cost else 0.0
        
        return breakdown


distribute = CRUDDistribute()
