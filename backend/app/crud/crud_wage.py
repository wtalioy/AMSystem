from typing import List, Optional

from app.dbrm import Session

from app.models import Wage as WageModel
from app.schemas import WageCreate, Wage


class CRUDWage:
    def get_by_type(self, db: Session, worker_type: str) -> Optional[Wage]:
        obj = db.query(WageModel).filter_by(worker_type=worker_type).first()
        if not obj:
            return None
        return Wage.model_validate(obj)
    
    def get_multi(self, db: Session) -> List[Wage]:
        objs = db.query(WageModel).all()
        if not objs:
            return []
        return [Wage.model_validate(obj) for obj in objs]
    
    def get_all_types(self, db: Session) -> List[str]:
        objs = db.query(WageModel).all()
        if not objs:
            return []
        return [obj.worker_type for obj in objs]
    
    def create(self, db: Session, *, obj_in: WageCreate) -> Wage:
        db_obj = WageModel(
            worker_type=obj_in.worker_type,
            wage_per_hour=obj_in.wage_per_hour
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return Wage.model_validate(db_obj)
    
    def update_wage_rate(
        self, db: Session, *, worker_type: str, new_wage_per_hour: int
    ) -> Wage:
        db_obj = self.get_by_type(db, worker_type=worker_type)
        if db_obj:
            db_obj.wage_per_hour = new_wage_per_hour
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return Wage.model_validate(db_obj)


wage = CRUDWage()
