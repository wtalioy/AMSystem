import random
import threading
import logging
from datetime import datetime, timedelta
from app.dbrm import Session
from app.core.database import get_db
from app.crud import order, worker
from app.core.enum import OrderStatus, WorkerAvailabilityStatus

logger = logging.getLogger(__name__)

# Global background processor instance
_background_processor = None


class AssignmentProcessor:
    """Unified background processor for automatic order assignment to available workers"""
    
    def __init__(self, interval_seconds: int = 30):
        self.interval_seconds = interval_seconds
        self.running = False
        self.thread = None
        self._stop_event = threading.Event()
    
    def start(self):
        """Start the assignment processor"""
        if self.running:
            return
        
        self.running = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run_processor, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the assignment processor"""
        if not self.running:
            return
        
        self.running = False
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
    
    def is_running(self) -> bool:
        """Check if assignment processor is running"""
        return self.running
    
    def _run_processor(self):
        """Main processor loop"""
        while self.running and not self._stop_event.is_set():
            try:
                # Use the database session with proper context management
                for db in get_db():
                    # Process pending assignments
                    result = self.process_pending_assignments(db)
                    
                    # Log only significant assignment activity (5+ orders)
                    if result >= 5:
                        logger.info(f"Assignment processor assigned {result} pending orders")
                    
                    # Also handle any stale assignments (assigned but not accepted)
                    self._handle_stale_assignments(db)
                    break  # Only process once per iteration
                
            except Exception as e:
                logger.error(f"Assignment processor error: {e}")
            
            # Wait for next interval or stop signal
            self._stop_event.wait(self.interval_seconds)
    
    def _handle_stale_assignments(self, db: Session):
        """Handle orders that have been assigned but not accepted for too long"""
        # Get orders that have been assigned for more than 10 minutes without acceptance
        stale_cutoff = datetime.now() - timedelta(minutes=10)
        
        try:
            stale_orders = order.get_stale_assigned_orders(db, cutoff_time=stale_cutoff)
            
            if stale_orders:
                logger.info(f"Processing {len(stale_orders)} stale assignments")
                
            for stale_order in stale_orders:
                # Reset to pending and let the system reassign
                order.update_order_assignment(db, order_id=stale_order.order_id, worker_id=None, status=OrderStatus.PENDING_ASSIGNMENT)
                # Free up the worker if they were marked as busy
                if stale_order.worker_id:
                    worker.update_availability(db, worker_id=stale_order.worker_id, status=WorkerAvailabilityStatus.AVAILABLE)
                
        except Exception as e:
            logger.error(f"Error handling stale assignments: {e}")
    
    def trigger_assignment(self, db: Session, order_id: str) -> bool:
        """Ultra-simple random assignment - no separate tracking needed"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj or order_obj.status != OrderStatus.PENDING_ASSIGNMENT:
            return False
        
        # Find all available workers
        available_workers = worker.get_available_workers(db)
        
        if not available_workers:
            # No workers available - order remains in PENDING_ASSIGNMENT
            # It will be processed when workers become available or by background processor
            return False
        
        # Random selection
        selected_worker = random.choice(available_workers)
        
        # Update order: assign worker, set status to assigned  
        order.update_order_assignment(db, order_id=order_id, worker_id=selected_worker.user_id, status=OrderStatus.ASSIGNED)
        
        # Update worker's availability status
        worker.update_availability(db, worker_id=selected_worker.user_id, status=WorkerAvailabilityStatus.BUSY)
        
        return True
    
    def process_pending_assignments(self, db: Session) -> int:
        """
        Process all pending order assignments and try to assign them to available workers.
        Returns the number of orders successfully assigned.
        """
        # Get all orders in PENDING_ASSIGNMENT status, prioritizing expedited orders
        pending_orders = order.get_orders_by_status(db, status=OrderStatus.PENDING_ASSIGNMENT)
        
        if not pending_orders:
            return 0
        
        # Sort pending orders by start_time
        sorted_orders = sorted(pending_orders, key=lambda o: o.start_time)
        
        assigned_count = 0
        
        for order_obj in sorted_orders:
            # Try to assign each pending order
            if self.trigger_assignment(db, order_obj.order_id):
                assigned_count += 1
            else:
                # No more available workers, stop processing
                break
        
        return assigned_count
    
    def get_assignment_statistics(self, db: Session) -> dict:
        """
        Get statistics about current assignment status for monitoring/debugging.
        """
        pending_orders = order.get_orders_by_status(db, status=OrderStatus.PENDING_ASSIGNMENT)
        available_workers = worker.get_available_workers(db)
        busy_workers = worker.get_workers_by_status(db, status=WorkerAvailabilityStatus.BUSY)
        
        expedited_pending = [o for o in pending_orders if o.expedite_flag]
        
        return {
            "pending_orders": len(pending_orders),
            "expedited_pending": len(expedited_pending),
            "available_workers": len(available_workers),
            "busy_workers": len(busy_workers),
            "assignment_capacity": len(available_workers) > 0,
            "background_processor_running": self.is_running()
        }


# Global instance management functions
def get_assignment_processor() -> AssignmentProcessor:
    """Get the global assignment processor instance"""
    global _background_processor
    if _background_processor is None:
        _background_processor = AssignmentProcessor()
    return _background_processor


def start_background_processor(interval_seconds: int = 30):
    """Start the global background assignment processor"""
    processor = get_assignment_processor()
    processor.interval_seconds = interval_seconds
    processor.start()


def stop_background_processor():
    """Stop the global background assignment processor"""
    global _background_processor
    if _background_processor:
        _background_processor.stop()


def is_background_processor_running() -> bool:
    """Check if the global background processor is running"""
    global _background_processor
    return _background_processor is not None and _background_processor.running


# Convenience functions for backward compatibility
def trigger_assignment(db: Session, order_id: str) -> bool:
    """Trigger assignment for a specific order"""
    return get_assignment_processor().trigger_assignment(db, order_id)


def process_pending_assignments(db: Session) -> int:
    """Process all pending assignments"""
    return get_assignment_processor().process_pending_assignments(db)


def get_assignment_statistics(db: Session) -> dict:
    """Get assignment statistics"""
    return get_assignment_processor().get_assignment_statistics(db)


def get_processor_status() -> dict:
    """Get processor status information"""
    global _background_processor
    if _background_processor is None:
        return {
            "running": False,
            "interval_seconds": None,
            "initialized": False
        }
    
    return {
        "running": _background_processor.running,
        "interval_seconds": _background_processor.interval_seconds,
        "initialized": True
    } 