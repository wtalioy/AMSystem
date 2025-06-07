import random
from typing import Optional
from app.dbrm import Session
from app.crud import order, worker
from app.core.enum import OrderStatus


class AutoAssignmentService:
    """Service for automatic order assignment to available workers"""
    
    @staticmethod
    def trigger_assignment(db: Session, order_id: str) -> bool:
        """Ultra-simple random assignment - no separate tracking needed"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj or order_obj.status != OrderStatus.PENDING_ASSIGNMENT:
            return False
        
        # Find all available workers
        available_workers = worker.get_available_workers(db)
        
        if not available_workers:
            return False
        
        # Random selection
        selected_worker = random.choice(available_workers)
        
        # Update order: assign worker, set status to assigned, set deadline
        order.update_order_assignment(db, order_id=order_id, worker_id=selected_worker.user_id, status=OrderStatus.ASSIGNED)  # assigned
        order.increment_assignment_attempts(db, order_id=order_id)  # This sets the deadline too
        
        # Update worker's current order count
        worker.update_order_count(db, worker_id=selected_worker.user_id, increment=1)
        
        return True
    
    @staticmethod
    def handle_rejection(db: Session, order_id: str, reason: Optional[str] = None) -> bool:
        """Handle order rejection and trigger reassignment"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj:
            return False
            
        # Save rejection reason and clear assignment
        if reason:
            order.set_rejection_reason(db, order_id=order_id, reason=reason)
        
        # Decrease worker's order count if they had been assigned
        if order_obj.worker_id:
            worker.update_order_count(db, worker_id=order_obj.worker_id, increment=-1)
        
        # Set order back to pending assignment
        order.update_order_assignment(db, order_id=order_id, worker_id=None, status=OrderStatus.PENDING_ASSIGNMENT)  # pending_assignment
        
        # Try to reassign to another worker
        return AutoAssignmentService.trigger_assignment(db, order_id)
    
    @staticmethod
    def handle_acceptance(db: Session, order_id: str, worker_id: str) -> bool:
        """Handle order acceptance - update status to in_progress"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj or order_obj.worker_id != worker_id:
            return False
        
        # Update order status to in_progress
        order.update_order_status(db, order_id=order_id, new_status=OrderStatus.IN_PROGRESS)  # in_progress
        
        return True 