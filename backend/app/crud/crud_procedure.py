from typing import List, Optional

from app.dbrm import Session

from app.crud.base import CRUDBase
from app.models.procedure import Procedure
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate


class CRUDProcedure(CRUDBase[Procedure, ProcedureCreate, ProcedureUpdate]):
    def get_by_id(self, db: Session, procedure_id: int) -> Optional[Procedure]:
        return db.query(Procedure).filter(Procedure.procedure_id == procedure_id).first()
    
    def get_procedures_by_order(
        self, db: Session, order_id: str
    ) -> List[Procedure]:
        return db.query(Procedure).filter_by(order_id=order_id).order_by(Procedure.procedure_id).all()
    
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
    
    def batch_update_procedure_status(
        self, db: Session, *, updates: List[dict]
    ) -> List[Optional[Procedure]]:
        """
        Batch update status for multiple procedures, implemented by updating each one 
        and committing once at the end
        
        Args:
            db: Database session
            updates: List containing update info, each element is {"procedure_id": id, "new_status": status}
            
        Returns:
            List[Optional[Procedure]]: List of updated procedure objects, None if a procedure doesn't exist
        """
        results = []
        
        # Start a transaction
        for update in updates:
            procedure_id = update.get("procedure_id")
            new_status = update.get("new_status")
            
            if procedure_id is None or new_status is None:
                results.append(None)
                continue
                
            db_obj = self.get_by_id(db, procedure_id=procedure_id)
            if not db_obj:
                results.append(None)
                continue
                
            # Update status, but don't commit immediately
            db_obj.current_status = new_status
            db.add(db_obj)
            results.append(db_obj)
        
        # Commit all changes at once
        db.commit()
        
        # Refresh all objects to get the latest data
        for obj in results:
            if obj:
                db.refresh(obj)
                
        return results


procedure = CRUDProcedure(Procedure)
