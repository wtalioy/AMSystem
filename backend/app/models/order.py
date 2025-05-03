from app.dbrm import Table, Column, Char, Text, Integer, Timestamp, Text, model_register

@model_register(dependencies=["Car", "Customer", "Worker"])
class Order(Table):
    __tablename__ = "Order"

    order_id = Column(Char(10), primary_key=True)
    start_time = Column(Timestamp, nullable=False)
    end_time = Column(Timestamp, nullable=True)
    description = Column(Text, nullable=False)
    rating = Column(Integer, check='BETWEEN 1 AND 5', nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(Integer, nullable=False, default=0)  # 0: pending, 1: in progress, 2: completed

    worker_id = Column(Char(10), foreign_key='Worker.user_id', nullable=False)
    car_id = Column(Char(10), foreign_key='Car.car_id', nullable=False)
    customer_id = Column(Char(10), foreign_key='Customer.user_id', nullable=False)