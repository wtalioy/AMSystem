"""
Application startup handlers and initialization
"""
import os
import logging
from app.dbrm import Session
from app.core.database import get_db

from app.background.earnings_scheduler import start_scheduler, stop_scheduler, get_scheduler
from app.background.assignment_processor import (
    process_pending_assignments, get_assignment_statistics,
    start_background_processor, stop_background_processor
)

logger = logging.getLogger(__name__)


def startup_background_services():
    """
    Initialize background services when the application starts
    """
    # Start earnings scheduler
    try:
        start_scheduler()
        logger.info("Earnings scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start earnings scheduler: {e}")
    
    # Start assignment processor
    # Get interval from environment variable or default to 30 seconds
    interval = int(os.getenv("ASSIGNMENT_PROCESSOR_INTERVAL", "30"))
    
    try:
        result = start_background_assignment_processor(interval_seconds=interval)
        logger.info(f"Assignment processor started with {interval}s interval - {result.get('pending_orders', 0)} pending orders, {result.get('available_workers', 0)} available workers")
    except Exception as e:
        logger.error(f"Failed to start assignment processor: {e}")


def shutdown_background_services():
    """
    Clean shutdown of background services when the application stops
    """
    # Stop earnings scheduler
    try:
        stop_scheduler()
        logger.info("Earnings scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop earnings scheduler: {e}")
    
    # Stop assignment processor
    try:
        result = stop_background_assignment_processor()
        logger.info("Assignment processor stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop assignment processor: {e}")


# Assignment system management functions
def start_background_assignment_processor(interval_seconds: int = 30) -> dict:
    """
    Start the background assignment processor.
    Returns current assignment statistics.
    """
    start_background_processor(interval_seconds)
    
    # Return current status
    for db in get_db():
        stats = get_assignment_statistics(db)
        stats["message"] = f"Assignment processor started with {interval_seconds}s interval"
        return stats


def stop_background_assignment_processor() -> dict:
    """
    Stop the background assignment processor.
    Returns final assignment statistics.
    """
    # Get stats before stopping
    for db in get_db():
        stats = get_assignment_statistics(db)
        break
    
    stop_background_processor()
    stats["background_processor_running"] = False
    stats["message"] = "Assignment processor stopped"
    
    return stats


def process_pending_assignments_admin(db: Session) -> dict:
    """
    Manually trigger processing of pending assignments.
    Useful for admin functions or periodic maintenance.
    Returns assignment statistics.
    """
    # Process pending assignments
    assigned_count = process_pending_assignments(db)
    
    # Get current statistics
    stats = get_assignment_statistics(db)
    stats["assignments_processed"] = assigned_count
    
    return stats


def get_assignment_system_status(db: Session) -> dict:
    """
    Get current assignment status for monitoring/debugging.
    """
    return get_assignment_statistics(db)


def get_system_health() -> dict:
    """
    Get current system health status including background services
    """
    try:
        for db in get_db():
            # Get assignment processor status
            assignment_stats = get_assignment_statistics(db)
            
            # Get earnings scheduler status
            scheduler = get_scheduler()
            scheduler_status = scheduler.get_scheduler_status()
            
            return {
                "status": "healthy" if (assignment_stats.get("background_processor_running", False) and scheduler_status.get("running", False)) else "degraded",
                "assignment_processor": {
                    "running": assignment_stats.get("background_processor_running", False),
                    "pending_orders": assignment_stats.get("pending_orders", 0),
                    "available_workers": assignment_stats.get("available_workers", 0),
                    "assignment_capacity": assignment_stats.get("assignment_capacity", False)
                },
                "earnings_scheduler": {
                    "running": scheduler_status.get("running", False),
                    "next_earnings_distribution": scheduler_status.get("next_earnings_distribution"),
                    "tasks_count": scheduler_status.get("tasks_count", 0)
                }
            }
    except Exception as e:
        logger.error(f"Error getting system health status: {e}")
        return {
            "status": "error",
            "error": str(e)
        } 