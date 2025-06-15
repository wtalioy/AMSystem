from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class PeriodCostBreakdown(BaseModel):
    """Schema for cost breakdown by period (month/quarter)"""
    period: str  # e.g., "2024-01" for month or "2024-Q1" for quarter
    material_cost: float
    labor_cost: float
    total_cost: float
    labor_material_ratio: float

    class Config:
        from_attributes = True


class VehicleFailurePattern(BaseModel):
    """Schema for vehicle failure pattern analysis"""
    car_type: str
    total_repairs: int
    common_issues: List[str]
    repair_frequency: int

    class Config:
        from_attributes = True


class CostAnalysisByPeriod(BaseModel):
    """Schema for cost analysis by time period"""
    period_start: str  # ISO format datetime
    period_end: str    # ISO format datetime
    total_material_cost: Decimal
    total_labor_cost: Decimal
    total_cost: Decimal
    labor_material_ratio: float
    period_breakdown: List[PeriodCostBreakdown]

    class Config:
        from_attributes = True


class LowRatedOrderData(BaseModel):
    """Schema for individual low-rated order data"""
    order_id: str
    rating: Optional[int]
    comment: Optional[str]
    worker_id: Optional[str]
    worker_type: Optional[str]
    completion_date: Optional[datetime]
    total_cost: Optional[Decimal]

    class Config:
        from_attributes = True


class WorkerPerformanceSummary(BaseModel):
    """Schema for worker performance summary in negative feedback analysis"""
    worker_id: str
    worker_type: Optional[str]
    low_rating_count: int
    total_completed_orders: int
    average_rating: float
    low_rating_percentage: float

    class Config:
        from_attributes = True


class NegativeFeedbackAnalysis(BaseModel):
    """Schema for negative feedback analysis response"""
    low_rated_orders: List[LowRatedOrderData]
    worker_performance_summary: List[WorkerPerformanceSummary]
    total_low_rated_orders: int

    class Config:
        from_attributes = True


class WorkerProductivityAnalysis(BaseModel):
    """Schema for worker productivity analysis"""
    worker_type: str
    total_tasks_assigned: int
    completed_tasks: int
    completion_rate_percentage: float
    average_completion_time_hours: float
    average_customer_rating: float
    productivity_score: float

    class Config:
        from_attributes = True


class WorkerStatistics(BaseModel):
    """Schema for worker statistics"""
    worker_type: str
    worker_count: int
    task_count: int
    total_work_hours: float
    average_hours_per_task: float
    hourly_wage: Decimal

    class Config:
        from_attributes = True


class CarTypeStatistics(BaseModel):
    """Schema for car type statistics"""
    car_type: str
    car_count: int
    repair_count: int
    average_repair_cost: Decimal
    repair_frequency: float

    class Config:
        from_attributes = True


class IncompleteOrderStatistics(BaseModel):
    """Schema for incomplete order statistics"""
    order_id: str
    car_id: str
    car_type: Optional[str]
    customer_id: str
    start_time: datetime
    description: str
    status: int
    procedures_count: int
    completed_procedures: int

    class Config:
        from_attributes = True 