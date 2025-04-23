from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.procedure import Procedure
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate


class CRUDProcedure(CRUDBase[Procedure, ProcedureCreate, ProcedureUpdate]):
    def get_by_id(self, db: Session, procedure_id: int) -> Optional[Procedure]:
        return db.query(Procedure).filter(Procedure.procedure_id == procedure_id).first()
    
    def get_procedures_by_order(
        self, db: Session, order_id: str
    ) -> List[Procedure]:
        return db.query(Procedure).filter(
            Procedure.order_id == order_id
        ).order_by(Procedure.procedure_id).all()
    
    def create_procedure_for_order(
        self, db: Session, *, obj_in: ProcedureCreate
    ) -> Procedure:
        db_obj = Procedure(
            order_id=obj_in.order_id,
            procedure_text=obj_in.procedure_text,
            current_status=obj_in.current_status
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_procedure_status(
        self, db: Session, *, procedure_id: int, new_status: int
    ) -> Procedure:
        db_obj = self.get_by_id(db, procedure_id=procedure_id)
        if db_obj:
            db_obj.current_status = new_status
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


procedure = CRUDProcedure(Procedure)
