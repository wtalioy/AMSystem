from typing import List, Optional
from decimal import Decimal
from app.dbrm import Session

from app.crud import car, order, log, user, procedure, distribute, worker, wage
from app.schemas import Distribute, OrderToAdmin, Order, DistributeCreate


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[OrderToAdmin]:
    """Get all orders (admin function)"""
    orders = order.get_multi(db, skip=skip, limit=limit)
    return [OrderToAdmin.model_validate(o) for o in orders]


def update_order_status(db: Session, order_id: str, new_status: int) -> Optional[Order]:
    """Update the status of an order"""
    order_obj = order.update_order_status(
        db=db, order_id=order_id, new_status=new_status
    )
    if order_obj:
        return Order.model_validate(order_obj)
    return None


def get_all_distributions(db: Session) -> List[Distribute]:
    """
    Get all distribution records
    """
    distributions = distribute.get_all_distributions(db)
    return [Distribute.model_validate(d) for d in distributions]


def get_car_type_statistics(db: Session) -> List[dict]:
    """
    Get statistics about car types, repairs, and costs
    """
    car_types = car.get_all_car_types(db)

    result = []
    for car_type, in car_types:
        car_count = car.count_cars_by_type(db, car_type)
        order_count = order.count_orders_by_car_type(db, car_type)
        avg_cost = log.calculate_avg_cost_by_car_type(db, car_type)
        repair_frequency = (order_count / car_count) * 100 if car_count > 0 else 0

        result.append({
            "car_type": car_type,
            "car_count": car_count,
            "repair_count": order_count,
            "average_repair_cost": avg_cost,
            "repair_frequency": repair_frequency
        })

    return result


def get_worker_statistics(db: Session, start_time: str, end_time: str) -> List[dict]:
    """
    Get statistics about worker types, their tasks, and productivity
    """
    worker_types = user.get_all_worker_types(db)

    result = []
    for worker_type, in worker_types:
        worker_count = user.count_workers_by_type(db, worker_type, start_time, end_time)
        task_count = log.count_tasks_by_worker_type(db, worker_type, start_time, end_time)
        total_hours = log.calculate_total_hours_by_worker_type(db, worker_type, start_time, end_time)

        wage_obj = wage.get_by_type(db, worker_type=worker_type)
        
        result.append({
            "worker_type": worker_type,
            "worker_count": worker_count,
            "task_count": task_count,
            "total_work_hours": total_hours,
            "average_hours_per_task": total_hours / task_count if task_count > 0 else 0,
            "hourly_wage": wage_obj.wage_per_hour if wage_obj else 0
        })
    
    return result


def get_incomplete_orders_statistics(db: Session) -> List[dict]:
    """
    Get all pending orders and their details
    """
    in_progress_orders = order.get_incomplete_orders(db)

    result = []
    for order_item in in_progress_orders:
        car_obj = car.get_by_car_id(db, car_id=order_item.car_id)

        progress_info = procedure.get_procedure_progress(db, order_id=order_item.order_id)
        completed_procedures = progress_info["completed"]
        total_procedures = progress_info["total"]
        
        result.append({
            "order_id": order_item.order_id,
            "car_id": order_item.car_id,
            "car_type": car_obj.car_type if car_obj else None,
            "customer_id": order_item.customer_id,
            "start_time": order_item.start_time,
            "description": order_item.description,
            "status": order_item.status,
            "procedures_count": total_procedures,
            "completed_procedures": completed_procedures,
        })
    
    return result


def distribute_payment(db: Session, worker_id: str, amount: Decimal) -> Distribute:
    """Record a payment distribution to a worker"""
    # Verify worker exists
    worker_obj = worker.get_by_id(db, worker_id=worker_id)
    if not worker_obj:
        raise ValueError("Worker does not exist")
    
    # Create distribution
    distribute_in = DistributeCreate(
        amount=amount,
        worker_id=worker_id
    )
    return Distribute.model_validate(
        distribute.create_distribution(db=db, obj_in=distribute_in)
    )
