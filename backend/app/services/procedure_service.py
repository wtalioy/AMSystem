from typing import List
from app.dbrm import Session

from app.core.enum import ProcedureStatus
from app.core.audit_decorators import audit
from app.crud import order, procedure
from app.schemas import Procedure, ProcedureCreate, ProcedureUpdate


class ProcedureService:
    """Service for procedure operations"""

    @staticmethod
    def get_procedure_progress(
        db: Session,
        order_id: str
    ) -> List[Procedure]:
        """Get all procedures for an order"""
        # Verify order exists
        order_obj = order.get_by_order_id(db, order_id=order_id)
        if not order_obj:
            raise ValueError("Order does not exist")
        
        # Get procedures for the order
        procedures = procedure.get_procedures_by_order(db, order_id=order_id)
        
        # Check if there are any procedures
        if not procedures:
            raise ValueError("No procedures found for this order")
        
        return procedures


    @staticmethod
    @audit("Procedure", "CREATE")
    def create_procedures(
        db: Session, 
        procedures: List[ProcedureCreate],
        worker_id: str
    ) -> List[Procedure]:
        """ Create maintenance procedures for an order """
        procedure_objs = []
        for procedure_in in procedures:       
            order_obj = order.get_by_order_id(db, order_id=procedure_in.order_id)
            if not order_obj:
                raise ValueError(f"Order with ID {procedure_in.order_id} does not exist")
            if order_obj.worker_id != worker_id:
                raise ValueError(f"Order {procedure_in.order_id} is not assigned to this worker")
            procedure_objs.append(procedure_in)

        created_procedures = procedure.create_procedures(db=db, obj_in_list=procedure_objs)
        return created_procedures


    @staticmethod
    @audit("Procedure", "UPDATE")
    def update_procedure_status(
        db: Session, 
        procedure_updates: List[ProcedureUpdate],
        worker_id: str
    ) -> List[Procedure]:
        """ Update the status of procedures """
        procedure_objs = []
        for procedure_update in procedure_updates:
            order_obj = order.get_by_order_id(db, order_id=procedure_update.order_id)
            procedure_obj = procedure.get_by_id(db, order_id=procedure_update.order_id, procedure_id=procedure_update.procedure_id)
            if order_obj.worker_id != worker_id:
                raise ValueError(f"Order {procedure_update.order_id} is not assigned to this worker")
            if not procedure_obj:
                raise ValueError(f"Procedure does not exist for order {procedure_update.order_id} and procedure {procedure_update.procedure_id}")
            if procedure_update.current_status not in [ProcedureStatus.PENDING, ProcedureStatus.IN_PROGRESS, ProcedureStatus.COMPLETED]:
                raise ValueError(f"Invalid status value: {procedure_update.current_status}, valid values are: {ProcedureStatus.PENDING}, {ProcedureStatus.IN_PROGRESS}, {ProcedureStatus.COMPLETED}")
            if procedure_update.current_status == procedure_obj.current_status:
                continue
            procedure_objs.append(procedure_update)
        
        updated_procedures = procedure.update_procedure_status(db=db, obj_ins=procedure_objs)
        return updated_procedures