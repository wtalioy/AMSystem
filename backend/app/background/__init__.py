"""
Background services module for AMSystem

This module provides background processing services including:
- Assignment processor for order assignment
- Earnings scheduler for periodic earnings distribution
"""

# Import all public functions from background services
from .assignment_processor import (
    process_pending_assignments,
    get_assignment_statistics,
    start_background_processor,
    stop_background_processor,
    trigger_assignment,
    get_processor_status
)

from .earnings_scheduler import (
    start_scheduler,
    stop_scheduler,
    get_scheduler,
    run_earnings_distribution_now
)

# Export all functions for easy importing
__all__ = [
    # Assignment processor functions
    'process_pending_assignments',
    'get_assignment_statistics', 
    'start_background_processor',
    'stop_background_processor',
    'trigger_assignment',
    'get_processor_status',
    
    # Earnings scheduler functions
    'start_scheduler',
    'stop_scheduler',
    'get_scheduler',
    'run_earnings_distribution_now'
] 