from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from app.dbrm import Session

from app.crud import order, log, wage, worker, car
from app.schemas import LogCreate, Log, OrderPending, Order
from app.core.enum import OrderStatus


class WorkerService:
    """Service for worker operations"""

    @staticmethod
    def create_maintenance_log(
        db: Session, 
        obj_in: LogCreate,
        worker_id: str
    ) -> Log:
        """Create a new maintenance log for an order"""
        order_obj = order.get_by_order_id(db, order_id=obj_in.order_id)
        if not order_obj:
            raise ValueError("Order does not exist")
        return log.create_log_for_order(db=db, obj_in=obj_in, worker_id=worker_id)


    @staticmethod
    def get_worker_logs(
        db: Session, worker_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        """Get all maintenance logs for a worker"""
        logs = log.get_logs_by_worker(db, worker_id=worker_id, skip=skip, limit=limit)
        return logs


    @staticmethod
    def get_pending_orders(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[OrderPending]:
        """Get all pending orders for workers"""
        pending_orders = order.get_orders_by_status(
            db,
            status=OrderStatus.PENDING_ASSIGNMENT,
            skip=skip,
            limit=limit
        )
    
        result = []
        for pending_order in pending_orders:
            car_info = car.get_by_car_id(db, car_id=pending_order.car_id)
            order_data = pending_order.model_dump()
            order_data["car_type"] = car_info.car_type if car_info else None
            enriched_order = OrderPending(**order_data)
            
            result.append(enriched_order)
        
        return result
    

    @staticmethod
    def get_wage_rate(db: Session, worker_type: str) -> Decimal:
        """Get the wage rate for a specific worker type"""
        wage_rate = wage.get_by_type(db, worker_type=worker_type)
        if not wage_rate:
            raise ValueError(f"No wage rate found for worker type {worker_type}")
        return wage_rate.wage_per_hour


    @staticmethod
    def accept_order(db: Session, order_id: str, worker_id: str) -> Dict:
        """Accept an assigned order and create procedures"""
        order_obj = order.get_by_order_id(db, order_id=order_id)
        if not order_obj:
            raise ValueError("Order not found")
        
        if order_obj.worker_id != worker_id:
            raise ValueError("Order is not assigned to this worker")
            
        if order_obj.status != OrderStatus.ASSIGNED:
            raise ValueError("Order is not in assigned state")
        
        # Handle acceptance through assignment service
        from app.services.assignment_service import AutoAssignmentService
        success = AutoAssignmentService.handle_acceptance(db, order_id=order_id, worker_id=worker_id)
        
        if not success:
            raise ValueError("Failed to accept order")
        
        return {"message": "Order accepted successfully", "order_id": order_id}


    @staticmethod
    def reject_order(db: Session, order_id: str, worker_id: str) -> Dict:
        """Reject an assigned order and trigger automatic reassignment"""
        order_obj = order.get_by_order_id(db, order_id=order_id)
        if not order_obj:
            raise ValueError("Order not found")
        
        if order_obj.worker_id != worker_id:
            raise ValueError("Order is not assigned to this worker")
            
        if order_obj.status != OrderStatus.ASSIGNED:
            raise ValueError("Order is not in assigned state")
        
        # Handle rejection through assignment service
        from app.services.assignment_service import AutoAssignmentService
        success = AutoAssignmentService.handle_rejection(db, order_id=order_id)
        
        if success:
            return {"message": "Order rejected and reassigned successfully", "order_id": order_id}
        else:
            return {"message": "Order rejected but no available workers for reassignment", "order_id": order_id}


    @staticmethod
    def get_assigned_orders(
        db: Session, worker_id: str, skip: int = 0, limit: int = 100, status: Optional[int] = None
    ) -> List[Order]:
        """Get orders assigned to a specific worker"""
        return order.get_orders_by_worker(db, worker_id=worker_id, skip=skip, limit=limit, status=status)


    @staticmethod
    def calculate_worker_earnings(
        db: Session, worker_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict:
        """Calculate worker earnings for a specified period"""
        worker_obj = worker.get_by_id(db, worker_id=worker_id)
        if not worker_obj:
            raise ValueError("Worker not found")
        
        # Get wage rate
        wage_rate = WorkerService.get_wage_rate(db, worker_type=worker_obj.worker_type)
        
        # Parse date range
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_dt = datetime.now() - timedelta(days=30)  # Default to last 30 days
            
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.now()
        
        # Get logs for the period (will need to implement these CRUD functions)
        # total_hours = log.get_total_duration_by_worker_period(
        #     db, worker_id=worker_id, start_date=start_dt, end_date=end_dt
        # )
        
        # For now, use existing function and note limitation
        total_hours = log.get_total_duration_by_worker(db, worker_id=worker_id)
        
        # Calculate earnings
        earnings = Decimal(str(total_hours)) * wage_rate
        
        # Get completed orders count (will need to implement)
        # completed_orders = order.get_completed_orders_count_by_worker_period(
        #     db, worker_id=worker_id, start_date=start_dt, end_date=end_dt
        # )
        completed_orders = 0  # Placeholder
        
        return {
            "worker_id": worker_id,
            "worker_type": worker_obj.worker_type,
            "period_start": start_dt.isoformat(),
            "period_end": end_dt.isoformat(),
            "hourly_rate": wage_rate,
            "total_hours": total_hours,
            "total_earnings": earnings,
            "orders_completed": completed_orders
        }
