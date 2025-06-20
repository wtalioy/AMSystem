from typing import List, Dict, Union
from datetime import datetime, timedelta
from decimal import Decimal
from calendar import monthrange
import logging

from app.dbrm import Session
from app.crud import order, log, worker, wage, distribute
from app.schemas import DistributeCreate
from app.schemas.earnings import (
    WorkerMonthlyEarnings, EarningsPeriod, WorkSummary, EarningsBreakdown,
    OrderDetail, MonthlyDistributionResults, DistributionDetail, DistributionError,
    EarningsReport, EarningsSummary, WorkerTypeSummary, FailedEarningsCalculation
)
from app.core.audit_decorators import audit

logger = logging.getLogger(__name__)


class EarningsService:
    """Service for calculating and distributing worker earnings"""

    @staticmethod
    def calculate_worker_monthly_earnings(
        db: Session, 
        worker_id: str, 
        year: int, 
        month: int
    ) -> WorkerMonthlyEarnings:
        """
        Calculate a worker's earnings for a specific month
        """
        # Get month boundaries
        start_date = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day, 23, 59, 59)
        
        # Get worker information
        worker_obj = worker.get_by_id(db, worker_id=worker_id)
        if not worker_obj:
            raise ValueError(f"Worker {worker_id} not found")
        
        # Get wage rate for this worker type
        wage_obj = wage.get_by_type(db, worker_type=worker_obj.worker_type)
        hourly_rate = Decimal(str(wage_obj.wage_per_hour)) if wage_obj else Decimal('0')
        
        # Get completed orders in this period
        completed_orders = order.get_completed_orders_by_worker_period(
            db, worker_id, start_date, end_date
        )
        
        # Calculate total hours worked from logs
        total_hours = Decimal('0')
        total_orders = 0
        order_details = []
        
        for order_obj in completed_orders:
            # Get logs for this order and worker
            order_logs = log.get_logs_by_order_and_worker(db, order_obj.order_id, worker_id)
            order_hours = sum(Decimal(str(log_entry.duration)) for log_entry in order_logs)
            
            total_hours += order_hours
            total_orders += 1
            
            order_details.append(OrderDetail(
                order_id=order_obj.order_id,
                completion_date=order_obj.end_time,
                hours_worked=float(order_hours),
                description=order_obj.description
            ))
        
        # Calculate earnings
        base_earnings = total_hours * hourly_rate
        
        # Performance bonus calculation (optional)
        # Based on customer ratings for completed orders
        avg_rating = order.get_average_rating_by_worker_period(db, worker_id, start_date, end_date)
        performance_bonus = Decimal('0')
        
        if avg_rating and avg_rating >= 4.5:
            performance_bonus = base_earnings * Decimal('0.1')  # 10% bonus for excellent ratings
        elif avg_rating and avg_rating >= 4.0:
            performance_bonus = base_earnings * Decimal('0.05')  # 5% bonus for good ratings
        
        total_earnings = base_earnings + performance_bonus
        
        return WorkerMonthlyEarnings(
            worker_id=worker_id,
            worker_type=worker_obj.worker_type,
            period=EarningsPeriod(
                year=year,
                month=month,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            ),
            work_summary=WorkSummary(
                total_hours=float(total_hours),
                total_orders=total_orders,
                hourly_rate=float(hourly_rate),
                average_rating=float(avg_rating) if avg_rating else None
            ),
            earnings=EarningsBreakdown(
                base_earnings=float(base_earnings),
                performance_bonus=float(performance_bonus),
                total_earnings=float(total_earnings)
            ),
            order_details=order_details
        )

    @staticmethod
    def calculate_all_workers_monthly_earnings(
        db: Session, 
        year: int, 
        month: int
    ) -> List[Union[WorkerMonthlyEarnings, FailedEarningsCalculation]]:
        """Calculate monthly earnings for all workers"""
        
        # Get all active workers
        all_workers = worker.get_all_workers(db)
        
        earnings_results = []
        for worker_obj in all_workers:
            try:
                earnings = EarningsService.calculate_worker_monthly_earnings(
                    db, worker_obj.user_id, year, month
                )
                earnings_results.append(earnings)
            except Exception as e:
                logger.error(f"Failed to calculate earnings for worker {worker_obj.user_id}: {e}")
                # Include failed calculation in results for transparency
                earnings_results.append(FailedEarningsCalculation(
                    worker_id=worker_obj.user_id,
                    error=str(e),
                    status="calculation_failed"
                ))
        
        return earnings_results

    @staticmethod
    @audit("Distribute", "CREATE")
    def distribute_worker_earnings(
        db: Session, 
        worker_id: str, 
        amount: Decimal, 
        audit_context=None
    ) -> bool:
        """
        Distribute (record payment) to a worker
        
        Args:
            db: Database session
            worker_id: Worker's user ID
            amount: Amount to distribute
            audit_context: Audit context for logging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify worker exists
            worker_obj = worker.get_by_id(db, worker_id=worker_id)
            if not worker_obj:
                logger.error(f"Worker {worker_id} not found for distribution")
                return False
            
            # Create distribution record
            distribute_data = DistributeCreate(
                amount=amount,
                worker_id=worker_id
            )
            
            distribution = distribute.create_distribution(db=db, obj_in=distribute_data)
            
            logger.info(f"Successfully distributed ${amount} to worker {worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to distribute earnings to worker {worker_id}: {e}")
            return False

    @staticmethod
    @audit("Distribute", "BULK_CREATE")
    def process_monthly_earnings_distribution(
        db: Session, 
        year: int, 
        month: int,
        audit_context=None
    ) -> MonthlyDistributionResults:
        """
        Process monthly earnings calculation and distribution for all workers
        
        This is the main method that should be called by the scheduler
        """
        logger.info(f"Starting monthly earnings distribution for {year}-{month:02d}")
        
        # Calculate earnings for all workers
        earnings_results = EarningsService.calculate_all_workers_monthly_earnings(db, year, month)
        
        distribution_details = []
        errors = []
        successful_distributions = 0
        failed_distributions = 0
        total_amount_distributed = Decimal('0')
        
        for earnings in earnings_results:
            if isinstance(earnings, FailedEarningsCalculation):
                # Skip workers with calculation errors
                failed_distributions += 1
                errors.append(DistributionError(
                    worker_id=earnings.worker_id,
                    error=earnings.error,
                    type="calculation_error"
                ))
                continue
            
            worker_id = earnings.worker_id
            total_earnings = Decimal(str(earnings.earnings.total_earnings))
            
            # Only distribute if there are earnings
            if total_earnings > 0:
                success = EarningsService.distribute_worker_earnings(
                    db, worker_id, total_earnings, audit_context
                )
                
                if success:
                    successful_distributions += 1
                    total_amount_distributed += total_earnings
                    distribution_details.append(DistributionDetail(
                        worker_id=worker_id,
                        amount=float(total_earnings),
                        hours_worked=earnings.work_summary.total_hours,
                        orders_completed=earnings.work_summary.total_orders
                    ))
                else:
                    failed_distributions += 1
                    errors.append(DistributionError(
                        worker_id=worker_id,
                        error="Distribution failed",
                        type="distribution_error"
                    ))
            else:
                # Worker had no earnings this period
                distribution_details.append(DistributionDetail(
                    worker_id=worker_id,
                    amount=0.0,
                    hours_worked=0.0,
                    orders_completed=0,
                    note="No earnings this period"
                ))
        
        logger.info(
            f"Monthly distribution complete: {successful_distributions} "
            f"successful, {failed_distributions} failed, "
            f"${total_amount_distributed} distributed"
        )
        
        return MonthlyDistributionResults(
            period=f"{year}-{month:02d}",
            total_workers=len(earnings_results),
            successful_distributions=successful_distributions,
            failed_distributions=failed_distributions,
            total_amount_distributed=float(total_amount_distributed),
            distribution_details=distribution_details,
            errors=errors
        )

    @staticmethod
    def get_worker_earnings_history(
        db: Session, 
        worker_id: str, 
        months_back: int = 12
    ) -> List[WorkerMonthlyEarnings]:
        """Get earnings history for a worker over the past N months"""
        
        earnings_history = []
        current_date = datetime.now()
        
        for i in range(months_back):
            # Calculate the month to check
            target_date = current_date - timedelta(days=30 * i)
            year = target_date.year
            month = target_date.month
            
            try:
                earnings = EarningsService.calculate_worker_monthly_earnings(
                    db, worker_id, year, month
                )
                earnings_history.append(earnings)
            except Exception as e:
                logger.warning(f"Could not calculate earnings for {worker_id} in {year}-{month}: {e}")
        
        return earnings_history

    @staticmethod
    def get_earnings_summary_report(
        db: Session, 
        year: int, 
        month: int
    ) -> EarningsReport:
        """Generate a summary report of earnings for all workers in a given month"""
        
        earnings_data = EarningsService.calculate_all_workers_monthly_earnings(db, year, month)
        
        # Filter out failed calculations
        valid_earnings = [e for e in earnings_data if isinstance(e, WorkerMonthlyEarnings)]
        
        if not valid_earnings:
            return EarningsReport(
                period=f"{year}-{month:02d}",
                total_workers=0
            )
        
        total_hours = sum(e.work_summary.total_hours for e in valid_earnings)
        total_earnings = sum(e.earnings.total_earnings for e in valid_earnings)
        total_orders = sum(e.work_summary.total_orders for e in valid_earnings)
        
        # Worker type breakdown
        worker_type_summary = {}
        for earnings in valid_earnings:
            wtype = earnings.worker_type
            if wtype not in worker_type_summary:
                worker_type_summary[wtype] = WorkerTypeSummary(
                    count=0,
                    total_hours=0,
                    total_earnings=0,
                    total_orders=0
                )
            
            worker_type_summary[wtype].count += 1
            worker_type_summary[wtype].total_hours += earnings.work_summary.total_hours
            worker_type_summary[wtype].total_earnings += earnings.earnings.total_earnings
            worker_type_summary[wtype].total_orders += earnings.work_summary.total_orders
        
        return EarningsReport(
            period=f"{year}-{month:02d}",
            total_workers=len(valid_earnings),
            summary=EarningsSummary(
                total_hours_worked=total_hours,
                total_earnings=total_earnings,
                total_orders_completed=total_orders,
                average_earnings_per_worker=total_earnings / len(valid_earnings) if valid_earnings else 0
            ),
            worker_type_breakdown=worker_type_summary
        ) 