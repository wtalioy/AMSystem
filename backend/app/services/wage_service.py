from typing import Optional
from app.dbrm import Session

from app.crud import wage
from app.schemas import Wage, WageCreate

class WageService:
    """Service for wage operations"""

    @staticmethod
    def get_wage_by_worker_type(db: Session, worker_type: str) -> Optional[Wage]:
        """Get wage rate for a specific worker type"""
        return wage.get_by_type(db, worker_type=worker_type)

    @staticmethod
    def create_wage(db: Session, obj_in: WageCreate) -> Wage:
        """Create a new wage rate"""
        return wage.create(db=db, obj_in=obj_in)

    @staticmethod
    def get_all_wages(db: Session) -> list[Wage]:
        """Get all wage rates"""
        return wage.get_multi(db=db)

    @staticmethod
    def update_wage_rate(db: Session, worker_type: str, new_wage_per_hour: int) -> Wage:
        """Update wage rate for a specific worker type"""
        return wage.update_wage_rate(db=db, worker_type=worker_type, new_wage_per_hour=new_wage_per_hour)
