from typing import Optional
from app.dbrm import Session

from app.crud import wage
from app.schemas import Wage

def get_wage_by_worker_type(db: Session, worker_type: str) -> Optional[Wage]:
    """Get wage rate for a specific worker type"""
    return Wage.model_validate(
        wage.get_by_type(db, worker_type=worker_type)
    )

def create_wage(db: Session, obj_in: Wage) -> Wage:
    """Create a new wage rate"""
    return Wage.model_validate(
        wage.create(db=db, obj_in=obj_in)
    )

def get_all_wages(db: Session) -> list[Wage]:
    """Get all wage rates"""
    return [Wage.model_validate(w) for w in wage.get_all(db=db)]

def update_wage_rate(db: Session, worker_type: str, new_wage_per_hour: int) -> Wage:
    """Update wage rate for a specific worker type"""
    return Wage.model_validate(
        wage.update_wage_rate(db=db, worker_type=worker_type, new_wage_per_hour=new_wage_per_hour)
    )
