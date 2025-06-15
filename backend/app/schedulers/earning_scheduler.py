import logging
from datetime import datetime
from typing import Optional, Dict, Any
import threading
import time

from app.api.deps import get_db
from app.services.earnings_service import EarningsService
from app.schemas.audit_log import ChangeTrackingContext

logger = logging.getLogger(__name__)


class EarningScheduler:
    """Service for managing scheduled tasks"""

    def __init__(self):
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.tasks = []

    def add_monthly_task(self, task_name: str, day_of_month: int, hour: int = 0, minute: int = 0):
        """Add a task to run monthly on a specific day"""
        self.tasks.append({
            "name": task_name,
            "type": "monthly",
            "day_of_month": day_of_month,
            "hour": hour,
            "minute": minute,
            "last_run": None
        })

    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        # Add default monthly earnings distribution task
        self.add_monthly_task("earnings_distribution", day_of_month=1, hour=2, minute=0)
        
        while self.running:
            try:
                current_time = datetime.now()
                
                for task in self.tasks:
                    if self._should_run_task(task, current_time):
                        self._execute_task(task, current_time)
                
                # Sleep for 60 seconds before checking again
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue after error

    def _should_run_task(self, task: Dict, current_time: datetime) -> bool:
        """Determine if a task should run based on its schedule"""
        if task["type"] == "monthly":
            # Check if it's the right day and time
            if (current_time.day == task["day_of_month"] and 
                current_time.hour == task["hour"] and 
                current_time.minute == task["minute"]):
                
                # Check if we haven't run this task this month
                last_run = task.get("last_run")
                if (not last_run or 
                    last_run.year != current_time.year or 
                    last_run.month != current_time.month):
                    return True
        
        return False

    def _execute_task(self, task: Dict, current_time: datetime):
        """Execute a scheduled task"""
        task_name = task["name"]
        logger.info(f"Executing scheduled task: {task_name}")
        
        try:
            if task_name == "earnings_distribution":
                self._run_monthly_earnings_distribution(current_time)
            
            # Update last run time
            task["last_run"] = current_time
            logger.info(f"Successfully completed task: {task_name}")
            
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")

    def _run_monthly_earnings_distribution(self, current_time: datetime):
        """Run the monthly earnings distribution for the previous month"""
        # Calculate previous month
        if current_time.month == 1:
            prev_month = 12
            prev_year = current_time.year - 1
        else:
            prev_month = current_time.month - 1
            prev_year = current_time.year
        
        # Get database session
        db = next(get_db())
        
        try:
            # Create audit context for the scheduler
            audit_context = ChangeTrackingContext(
                user_id="SCHEDULER"
            )
            
            # Process monthly earnings
            result = EarningsService.process_monthly_earnings_distribution(
                db=db, 
                year=prev_year, 
                month=prev_month,
                audit_context=audit_context
            )
            
            logger.info(
                f"Monthly earnings distribution completed for {prev_year}-{prev_month:02d}: "
                f"{result.successful_distributions} successful, "
                f"{result.failed_distributions} failed, "
                f"${result.total_amount_distributed} distributed"
            )
            
        except Exception as e:
            logger.error(f"Failed to run monthly earnings distribution: {e}")
        finally:
            db.close()

    def run_earnings_distribution_now(self, year: int, month: int) -> Dict[str, Any]:
        """Manually trigger earnings distribution for a specific month"""
        logger.info(f"Manually running earnings distribution for {year}-{month:02d}")
        
        db = next(get_db())
        
        try:
            audit_context = ChangeTrackingContext(
                user_id="MANUAL"
            )
            
            result = EarningsService.process_monthly_earnings_distribution(
                db=db, 
                year=year, 
                month=month,
                audit_context=audit_context
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to manually run earnings distribution: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
        finally:
            db.close()

    def get_next_scheduled_run(self) -> Optional[datetime]:
        """Get the next scheduled earnings distribution run time"""
        current_time = datetime.now()
        
        # Calculate next month's first day at 2 AM
        if current_time.month == 12:
            next_month = 1
            next_year = current_time.year + 1
        else:
            next_month = current_time.month + 1
            next_year = current_time.year
        
        next_run = datetime(next_year, next_month, 1, 2, 0, 0)
        
        # If we're past the scheduled time this month, it's next month
        this_month_scheduled = datetime(current_time.year, current_time.month, 1, 2, 0, 0)
        if current_time > this_month_scheduled:
            return next_run
        else:
            return this_month_scheduled

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "running": self.running,
            "next_earnings_distribution": self.get_next_scheduled_run().isoformat() if self.get_next_scheduled_run() else None,
            "tasks_count": len(self.tasks),
            "tasks": [
                {
                    "name": task["name"],
                    "type": task["type"],
                    "last_run": task["last_run"].isoformat() if task["last_run"] else None
                }
                for task in self.tasks
            ]
        }


# Global scheduler instance
scheduler = EarningScheduler()


def start_scheduler():
    """Start the global scheduler instance"""
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler instance"""
    scheduler.stop()


def get_scheduler() -> EarningScheduler:
    """Get the global scheduler instance"""
    return scheduler 