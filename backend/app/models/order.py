from app.dbrm import Table, Column, Char, Text, Integer, Timestamp, Text, Decimal, Boolean, model_register
from app.core.enum import OrderStatus

@model_register(dependencies=["Car", "Customer", "Worker"])
class ServiceOrder(Table):
    __tablename__ = "ServiceOrder"

    order_id = Column(Char(10), nullable=False, primary_key=True)
    start_time = Column(Timestamp, nullable=False)
    end_time = Column(Timestamp, nullable=True)
    description = Column(Text, nullable=False)
    rating = Column(Integer, check='BETWEEN 1 AND 5', nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(Integer, nullable=False, default=OrderStatus.PENDING_ASSIGNMENT)
    total_cost = Column(Decimal(10, 2), nullable=True)  # Auto-calculated when completed
    expedite_flag = Column(Boolean, nullable=False, default=False)  # Customer expedite request
    
    # New assignment tracking fields
    assignment_attempts = Column(Integer, nullable=False, default=0)
    last_assignment_at = Column(Timestamp, nullable=True)

    worker_id = Column(Char(10), foreign_key='Worker.user_id', nullable=True, on_delete="SET NULL", on_update="CASCADE", index=True)
    car_id = Column(Char(10), foreign_key='Car.car_id', nullable=False, on_delete="CASCADE", on_update="CASCADE", index=True)
    customer_id = Column(Char(10), foreign_key='Customer.user_id', nullable=False, on_delete="CASCADE", on_update="CASCADE", index=True)