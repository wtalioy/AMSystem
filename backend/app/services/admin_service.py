from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from app.dbrm import Session

from app.crud import car, order, log, user, procedure, distribute, worker, wage
from app.schemas import (
    Distribute, Order, DistributeCreate,
    VehicleFailurePattern,
    CostAnalysisByPeriod,
    LowRatedOrderData,
    WorkerPerformanceSummary,
    NegativeFeedbackAnalysis,
    WorkerProductivityAnalysis,
    WorkerStatistics,
    CarTypeStatistics,
    IncompleteOrderStatistics,
)


class AdminService:
    """Service for admin functions"""

    @staticmethod
    def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders (admin function)"""
        orders = order.get_multi(db, skip=skip, limit=limit)
        return orders

    @staticmethod
    def update_order_status(db: Session, order_id: str, new_status: int) -> Optional[Order]:
        """Update the status of an order"""
        order_obj = order.update_order_status(
            db=db, order_id=order_id, new_status=new_status
        )
        return order_obj


    @staticmethod
    def get_all_distributions(db: Session) -> List[Distribute]:
        """
        Get all distribution records
        """
        distributions = distribute.get_all_distributions(db)
        return distributions


    @staticmethod
    def get_car_type_statistics(db: Session) -> List[CarTypeStatistics]:
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

            stats = CarTypeStatistics(
                car_type=car_type,
                car_count=car_count,
                repair_count=order_count,
                average_repair_cost=avg_cost,
                repair_frequency=repair_frequency
            )
            result.append(stats)

        return result


    @staticmethod
    def get_vehicle_failure_patterns(db: Session) -> List[VehicleFailurePattern]:
        """
        Analyze most common failure types by vehicle type
        """
        # Get all car types
        car_types = car.get_all_car_types(db)
        
        result = []
        for car_type, in car_types:
            # Get most common descriptions/issues for this car type
            failure_patterns = order.get_failure_patterns_by_car_type(db, car_type)
            
            pattern = VehicleFailurePattern(
                car_type=car_type,
                total_repairs=len(failure_patterns),
                common_issues=failure_patterns[:5],  # Top 5 most common
                repair_frequency=order.count_orders_by_car_type(db, car_type)
            )
            result.append(pattern)
        
        return result


    @staticmethod
    def get_cost_analysis_by_period(
        db: Session, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        period_type: str = "month"
    ) -> CostAnalysisByPeriod:
        """
        Analyze costs by time period with labor vs materials breakdown
        """
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_dt = datetime.now() - timedelta(days=90)  # Default 3 months
            
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.now()
        
        # Get cost breakdown for the period
        total_material_cost = log.get_total_material_cost_by_period(db, start_dt, end_dt)
        total_labor_cost = log.get_total_labor_cost_by_period(db, start_dt, end_dt)
        
        # Get monthly/quarterly breakdown
        period_breakdown = log.get_cost_breakdown_by_period(db, start_dt, end_dt, period_type)
        
        return CostAnalysisByPeriod(
            period_start=start_dt.isoformat(),
            period_end=end_dt.isoformat(),
            total_material_cost=total_material_cost,
            total_labor_cost=total_labor_cost,
            total_cost=total_material_cost + total_labor_cost,
            labor_material_ratio=(total_labor_cost / total_material_cost) if total_material_cost > 0 else 0,
            period_breakdown=period_breakdown
        )


    @staticmethod
    def get_negative_feedback_analysis(db: Session, rating_threshold: int = 3) -> NegativeFeedbackAnalysis:
        """
        Analyze orders with low ratings and associated workers
        """
        low_rated_orders = order.get_orders_by_rating_threshold(db, rating_threshold)
        
        low_rated_order_data = []
        worker_feedback_summary = {}
        
        for order_item in low_rated_orders:
            # Get worker info
            worker_obj = worker.get_by_id(db, worker_id=order_item.worker_id) if order_item.worker_id else None
            
            order_data = LowRatedOrderData(
                order_id=order_item.order_id,
                rating=order_item.rating,
                comment=order_item.comment,
                worker_id=order_item.worker_id,
                worker_type=worker_obj.worker_type if worker_obj else None,
                completion_date=order_item.end_time,
                total_cost=order_item.total_cost
            )
            low_rated_order_data.append(order_data)
            
            # Track worker performance
            if order_item.worker_id:
                if order_item.worker_id not in worker_feedback_summary:
                    worker_feedback_summary[order_item.worker_id] = {
                        "worker_id": order_item.worker_id,
                        "worker_type": worker_obj.worker_type if worker_obj else None,
                        "low_rating_count": 0,
                        "total_completed_orders": 0,
                        "average_rating": 0.0,
                        "low_rating_percentage": 0.0
                    }
                worker_feedback_summary[order_item.worker_id]["low_rating_count"] += 1
        
        # Calculate worker performance metrics
        worker_performance_list = []
        for worker_id in worker_feedback_summary:
            total_orders = order.count_completed_orders_by_worker(db, worker_id)
            avg_rating = order.get_average_rating_by_worker(db, worker_id)
            low_rating_count = worker_feedback_summary[worker_id]["low_rating_count"]
            
            performance = WorkerPerformanceSummary(
                worker_id=worker_id,
                worker_type=worker_feedback_summary[worker_id]["worker_type"],
                low_rating_count=low_rating_count,
                total_completed_orders=total_orders,
                average_rating=avg_rating,
                low_rating_percentage=(low_rating_count / total_orders * 100) if total_orders > 0 else 0
            )
            worker_performance_list.append(performance)
        
        return NegativeFeedbackAnalysis(
            low_rated_orders=low_rated_order_data,
            worker_performance_summary=worker_performance_list,
            total_low_rated_orders=len(low_rated_order_data)
        )


    @staticmethod
    def get_worker_productivity_analysis(
        db: Session,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[WorkerProductivityAnalysis]:
        """
        Analyze worker productivity metrics by specialty
        """
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_dt = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") 
        else:
            end_dt = datetime.now()
        
        worker_types = user.get_all_worker_types(db)
        
        result = []
        for worker_type, in worker_types:
            # Get productivity metrics for this worker type
            completion_rate = order.get_completion_rate_by_worker_type(db, worker_type, start_dt, end_dt)
            avg_completion_time = order.get_average_completion_time_by_worker_type(db, worker_type, start_dt, end_dt)
            customer_satisfaction = order.get_average_rating_by_worker_type(db, worker_type, start_dt, end_dt)
            
            # Get task distribution
            total_tasks = order.count_orders_by_worker_type(db, worker_type, start_dt, end_dt)
            completed_tasks = order.count_completed_orders_by_worker_type(db, worker_type, start_dt, end_dt)
            
            productivity = WorkerProductivityAnalysis(
                worker_type=worker_type,
                total_tasks_assigned=total_tasks,
                completed_tasks=completed_tasks,
                completion_rate_percentage=completion_rate,
                average_completion_time_hours=avg_completion_time,
                average_customer_rating=customer_satisfaction,
                productivity_score=(completion_rate * customer_satisfaction) / 5 if customer_satisfaction else 0
            )
            result.append(productivity)
        
        return result


    @staticmethod
    def get_worker_statistics(db: Session, start_time: str, end_time: str) -> List[WorkerStatistics]:
        """
        Get statistics about worker types, their tasks, and productivity
        """
        worker_types = worker.get_all_worker_types(db)

        result = []
        for worker_type in worker_types:
            worker_count = worker.count_workers_by_type(db, worker_type, start_time, end_time)
            task_count = log.count_tasks_by_worker_type(db, worker_type, start_time, end_time)
            total_hours = log.calculate_total_hours_by_worker_type(db, worker_type, start_time, end_time)

            wage_obj = wage.get_by_type(db, worker_type=worker_type)
            
            stats = WorkerStatistics(
                worker_type=worker_type,
                worker_count=worker_count,
                task_count=task_count,
                total_work_hours=total_hours,
                average_hours_per_task=total_hours / task_count if task_count > 0 else 0,
                hourly_wage=wage_obj.wage_per_hour if wage_obj else Decimal('0')
            )
            result.append(stats)
        
        return result


    @staticmethod
    def get_incomplete_orders_statistics(db: Session) -> List[IncompleteOrderStatistics]:
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
            
            stats = IncompleteOrderStatistics(
                order_id=order_item.order_id,
                car_id=order_item.car_id,
                car_type=car_obj.car_type if car_obj else None,
                customer_id=order_item.customer_id,
                start_time=order_item.start_time,
                description=order_item.description,
                status=order_item.status,
                procedures_count=total_procedures,
                completed_procedures=completed_procedures,
            )
            result.append(stats)
        
        return result


    @staticmethod
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
        return distribute.create_distribution(db=db, obj_in=distribute_in)
