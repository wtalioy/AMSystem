from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.wage import Wage
from app.schemas.wage import WageCreate, WageUpdate


class CRUDWage(CRUDBase[Wage, WageCreate, WageUpdate]):
    def get_by_type(self, db: Session, worker_type: int) -> Optional[Wage]:
        return db.query(Wage).filter(Wage.worker_type == worker_type).first()
    
    def get_all_wages(self, db: Session) -> List[Wage]:
        return db.query(Wage).all()
    
    def create_wage(self, db: Session, *, obj_in: WageCreate) -> Wage:
        db_obj = Wage(
            worker_type=obj_in.worker_type,
            wage_per_hour=obj_in.wage_per_hour
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_wage_rate(
        self, db: Session, *, worker_type: int, new_wage_per_hour: int
    ) -> Wage:
        db_obj = self.get_by_type(db, worker_type=worker_type)
        if db_obj:
            db_obj.wage_per_hour = new_wage_per_hour
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


wage = CRUDWage(Wage)
