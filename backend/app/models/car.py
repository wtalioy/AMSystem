from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Car(Base):
    car_id = Column(String(10), primary_key=True, index=True)
    car_type = Column(Integer, nullable=False)
    customer_id = Column(String(10), ForeignKey('customer.user_id'))
    
    # 关系
    customer = relationship("Customer", back_populates="cars")
    orders = relationship("Order", back_populates="car")
