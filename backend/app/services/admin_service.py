from typing import List
from app.dbrm import Session

from app.crud import car, order, log, user, procedure, distribute
from app.schemas import Distribute


def get_all_distributions(db: Session) -> List[Distribute]:
    """
    Get all distribution records
    """
    distributions = distribute.get_all_distributions(db)
    return distributions


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

        wage = wage.get_by_type(db, worker_type=worker_type)
        
        result.append({
            "worker_type": worker_type,
            "worker_count": worker_count,
            "task_count": task_count,
            "total_work_hours": total_hours,
            "average_hours_per_task": total_hours / task_count if task_count > 0 else 0,
            "hourly_wage": wage.wage_per_hour if wage else 0
        })
    
    return result


def get_incomplete_orders_statistics(db: Session) -> List[dict]:
    """
    Get all pending orders and their details
    """
    in_progress_orders = order.get_incomplete_orders(db)

    result = []
    for order_item in in_progress_orders:
        car = car.get_by_car_id(db, car_id=order_item.car_id)

        progress_info = procedure.get_procedure_progress(db, order_id=order_item.order_id)
        completed_procedures = progress_info["completed"]
        total_procedures = progress_info["total"]
        
        result.append({
            "order_id": order_item.order_id,
            "car_id": order_item.car_id,
            "car_type": car.car_type if car else None,
            "customer_id": order_item.customer_id,
            "start_time": order_item.start_time,
            "description": order_item.description,
            "status": order_item.status,
            "procedures_count": total_procedures,
            "completed_procedures": completed_procedures,
        })
    
    return result
