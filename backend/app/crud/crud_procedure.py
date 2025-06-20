from typing import List, Optional, Dict

from app.dbrm import Session

from app.models import ServiceProcedure as ServiceProcedureModel
from app.schemas import ProcedureCreate, ProcedureUpdate, Procedure
from app.core.enum import ProcedureStatus


class CRUDProcedure:
    def get_by_id(self, db: Session, order_id: str, procedure_id: int) -> Optional[Procedure]:
        obj = db.query(ServiceProcedureModel).filter_by(order_id=order_id, procedure_id=procedure_id).first()
        if not obj:
            return None
        return Procedure.model_validate(obj)
    
    
    def get_procedures_by_order(
        self, db: Session, order_id: str
    ) -> List[Procedure]:
        objs = db.query(ServiceProcedureModel).filter_by(order_id=order_id).order_by(ServiceProcedureModel.procedure_id).all()
        if not objs:
            return []
        return [Procedure.model_validate(obj) for obj in objs]
    

    def create_procedures(
        self, db: Session, *, obj_in_list: List[ProcedureCreate]
    ) -> List[Procedure]:
        from app.dbrm import func
        order_id = obj_in_list[0].order_id
        last_procedure_id = db.query(func.max(ServiceProcedureModel.procedure_id)).filter_by(order_id=order_id).scalar() or 0
        
        db_objs = []
        for i, obj_in in enumerate(obj_in_list):
            db_obj = ServiceProcedureModel(
                order_id=order_id,
                procedure_text=obj_in.procedure_text,
                current_status=ProcedureStatus.PENDING,
                procedure_id=last_procedure_id + i + 1
            )
            db.add(db_obj)
            db_objs.append(db_obj)
        
        db.commit()
        
        for obj in db_objs:
            db.refresh(obj)
                
        return db_objs
    

    def update_procedure_status(
        self, db: Session, obj_ins: List[ProcedureUpdate]
    ) -> List[Procedure]:
        db_objs = []
        
        for obj_in in obj_ins:
            db_obj = ServiceProcedureModel(
                order_id=obj_in.order_id,
                procedure_id=obj_in.procedure_id,
                current_status=obj_in.current_status
            )
            db.add(db_obj)
            db_objs.append(db_obj)
        
        db.commit()
        
        for obj in db_objs:
            db.refresh(obj)
                
        return [Procedure.model_validate(obj) for obj in db_objs]
    

    def get_procedure_progress(self, db: Session, order_id: str) -> Dict[str, int]:
        procedures = self.get_procedures_by_order(db, order_id=order_id) or []
        
        completed_procedures = sum(1 for p in procedures if p.current_status == 2)
        total_procedures = len(procedures)
        
        return {
            "total": total_procedures,
            "completed": completed_procedures
        }


procedure = CRUDProcedure()
