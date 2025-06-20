import logging
from datetime import datetime
from typing import Optional, Dict, Any
import threading
import time

from app.dbrm import Session
from app.core.database import get_db
from app.services.earnings_service import EarningsService
from app.schemas.audit_log import ChangeTrackingContext

logger = logging.getLogger(__name__)

# Global earnings scheduler instance
_background_scheduler = None


class EarningScheduler:
    """Service for managing scheduled tasks"""

    def __init__(self):
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.tasks = []
        self._stop_event = threading.Event()

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
            self._stop_event.clear()
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()

    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.running = False
        self._stop_event.set()
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def is_running(self) -> bool:
        """Check if the scheduler is running"""
        return self.running

    def _run_scheduler(self):
        """Main scheduler loop"""
        # Add default monthly earnings distribution task
        self.add_monthly_task("earnings_distribution", day_of_month=1, hour=2, minute=0)
        
        while self.running and not self._stop_event.is_set():
            try:
                current_time = datetime.now()
                
                for task in self.tasks:
                    if self._should_run_task(task, current_time):
                        self._execute_task(task, current_time)
                
                # Wait for 60 seconds or until stop signal
                self._stop_event.wait(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Wait briefly before continuing after error
                self._stop_event.wait(60)

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
            # Get database session for the task
            for db in get_db():
                if task_name == "earnings_distribution":
                    self._run_monthly_earnings_distribution(db, current_time)
                
                # Update last run time
                task["last_run"] = current_time
                logger.info(f"Successfully completed task: {task_name}")
                break
            
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")

    def _run_monthly_earnings_distribution(self, db: Session, current_time: datetime):
        """Run the monthly earnings distribution for the previous month"""
        # Calculate previous month
        if current_time.month == 1:
            prev_month = 12
            prev_year = current_time.year - 1
        else:
            prev_month = current_time.month - 1
            prev_year = current_time.year
        
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
            raise  # Re-raise to be handled by _execute_task

    def run_earnings_distribution_now(self, db: Session, year: int, month: int) -> Dict[str, Any]:
        """Manually trigger earnings distribution for a specific month"""
        logger.info(f"Manually running earnings distribution for {year}-{month:02d}")
        
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
            
            # Update the scheduled task's last_run time to prevent duplicate automatic execution
            for task in self.tasks:
                if task["name"] == "earnings_distribution":
                    if month == 12:
                        next_month = 1
                        next_year = year + 1
                    else:
                        next_month = month + 1
                        next_year = year
                    
                    task["last_run"] = datetime(next_year, next_month, 1, task["hour"], task["minute"])
                    logger.info(f"Updated scheduled task last_run to prevent duplicate execution for {year}-{month:02d}")
                    break
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to manually run earnings distribution: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }

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


def start_scheduler():
    """Start the global scheduler instance"""
    global _background_scheduler
    if _background_scheduler is None:
        _background_scheduler = EarningScheduler()
    _background_scheduler.start()


def stop_scheduler():
    """Stop the global scheduler instance"""
    global _background_scheduler
    if _background_scheduler is not None:
        _background_scheduler.stop()


def get_scheduler() -> EarningScheduler:
    """Get the global scheduler instance"""
    global _background_scheduler
    if _background_scheduler is None:
        _background_scheduler = EarningScheduler()
    return _background_scheduler


# Convenience function for manual earnings distribution
def run_earnings_distribution_now(db: Session, year: int, month: int) -> Dict[str, Any]:
    """Manually trigger earnings distribution for a specific month"""
    scheduler = get_scheduler()
    return scheduler.run_earnings_distribution_now(db, year, month) 