from typing import List, Optional, Dict

from app.dbrm import Session

from app.crud.base import CRUDBase
from app.models.procedure import ServiceProcedure
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate


class CRUDProcedure(CRUDBase[ServiceProcedure, ProcedureCreate, ProcedureUpdate]):
    def get_by_id(self, db: Session, procedure_id: int) -> Optional[ServiceProcedure]:
        return db.query(ServiceProcedure).filter(ServiceProcedure.procedure_id == procedure_id).first()
    
    
    def get_procedures_by_order(
        self, db: Session, order_id: str
    ) -> List[ServiceProcedure]:
        return db.query(ServiceProcedure).filter_by(order_id=order_id).order_by(ServiceProcedure.procedure_id).all()
    

    def create_procedure_for_order(
        self, db: Session, *, obj_in: ProcedureCreate
    ) -> ServiceProcedure:
        db_obj = ServiceProcedure(
            order_id=obj_in.order_id,
            procedure_text=obj_in.procedure_text,
            current_status=obj_in.current_status
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    def create_procedures(
        self, db: Session, *, obj_in_list: List[ProcedureCreate]
    ) -> List[ServiceProcedure]:
        """
        Batch create multiple procedures for orders
        
        Args:
            db: Database session
            obj_in_list: List of ProcedureCreate objects to create
            
        Returns:
            List[Procedure]: List of created procedure objects
        """
        db_objs = []
        
        # Create all procedure objects but don't commit yet
        for obj_in in obj_in_list:
            db_obj = ServiceProcedure(
                order_id=obj_in.order_id,
                procedure_text=obj_in.procedure_text,
                current_status=obj_in.current_status
            )
            db.add(db_obj)
            db_objs.append(db_obj)
        
        # Commit all at once
        db.commit()
        
        # Refresh all objects to get the latest data
        for obj in db_objs:
            db.refresh(obj)
                
        return db_objs
    

    def update_procedure_status(
        self, db: Session, *, updates: List[dict]
    ) -> List[Optional[ServiceProcedure]]:
        """
        Update status for procedures, implemented by updating each one
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
    

    def get_procedure_progress(self, db: Session, order_id: str) -> Dict[str, int]:
        procedures = self.get_procedures_by_order(db, order_id=order_id) or []
        
        completed_procedures = sum(1 for p in procedures if p.current_status == 2)
        total_procedures = len(procedures)
        
        return {
            "total": total_procedures,
            "completed": completed_procedures
        }


procedure = CRUDProcedure(ServiceProcedure)
