from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey, CheckConstraint, text
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Order(Base):
    order_id = Column(String(10), primary_key=True, index=True)
    start_time = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    end_time = Column(TIMESTAMP, nullable=True)
    description = Column(Text, nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(Integer, nullable=False, default=0)  # 0: 待分配, 1: 进行中, 2: 已完成
    
    # 外键关系
    car_id = Column(String(10), ForeignKey('car.car_id'), nullable=False)
    customer_id = Column(String(10), ForeignKey('customer.user_id'), nullable=False)
    
    # 关系
    car = relationship("Car", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    logs = relationship("Log", back_populates="order")
    procedures = relationship("Procedure", back_populates="order")
