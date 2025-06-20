from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class EarningsPeriod(BaseModel):
    """Schema for earnings calculation period"""
    year: int
    month: int
    start_date: str  # ISO format datetime
    end_date: str    # ISO format datetime

    class Config:
        from_attributes = True


class WorkSummary(BaseModel):
    """Schema for work summary in earnings calculation"""
    total_hours: float
    total_orders: int
    hourly_rate: float
    average_rating: Optional[float]

    class Config:
        from_attributes = True


class EarningsBreakdown(BaseModel):
    """Schema for earnings breakdown"""
    base_earnings: float
    performance_bonus: float
    total_earnings: float

    class Config:
        from_attributes = True


class OrderDetail(BaseModel):
    """Schema for individual order details in earnings"""
    order_id: str
    completion_date: Optional[datetime]
    hours_worked: float
    description: str

    class Config:
        from_attributes = True


class WorkerMonthlyEarnings(BaseModel):
    """Schema for worker monthly earnings calculation"""
    worker_id: str
    worker_type: str
    period: EarningsPeriod
    work_summary: WorkSummary
    earnings: EarningsBreakdown
    order_details: List[OrderDetail]

    class Config:
        from_attributes = True


class DistributionDetail(BaseModel):
    """Schema for individual distribution detail"""
    worker_id: str
    amount: float
    hours_worked: float
    orders_completed: int
    note: Optional[str] = None

    class Config:
        from_attributes = True


class DistributionError(BaseModel):
    """Schema for distribution error"""
    worker_id: str
    error: str
    type: str  # "calculation_error" or "distribution_error"

    class Config:
        from_attributes = True


class MonthlyDistributionResults(BaseModel):
    """Schema for monthly distribution results"""
    period: str
    total_workers: int
    successful_distributions: int
    failed_distributions: int
    total_amount_distributed: float
    distribution_details: List[DistributionDetail]
    errors: List[DistributionError]

    class Config:
        from_attributes = True


class EarningsSummary(BaseModel):
    """Schema for earnings summary statistics"""
    total_hours_worked: float
    total_earnings: float
    total_orders_completed: int
    average_earnings_per_worker: float

    class Config:
        from_attributes = True


class WorkerTypeSummary(BaseModel):
    """Schema for worker type breakdown in summary"""
    count: int
    total_hours: float
    total_earnings: float
    total_orders: int

    class Config:
        from_attributes = True


class EarningsReport(BaseModel):
    """Schema for earnings summary report"""
    period: str
    total_workers: int
    summary: Optional[EarningsSummary] = None
    worker_type_breakdown: Optional[dict[str, WorkerTypeSummary]] = None

    class Config:
        from_attributes = True


class FailedEarningsCalculation(BaseModel):
    """Schema for failed earnings calculation"""
    worker_id: str
    error: str
    status: str = "calculation_failed"

    class Config:
        from_attributes = True 