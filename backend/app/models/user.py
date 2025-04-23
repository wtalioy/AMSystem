from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class User(Base):
    id = Column(String(10), primary_key=True, index=True)
    user_name = Column(String(10), nullable=False)
    user_pwd = Column(String(100), nullable=False)  # 存储哈希后的密码
    user_type = Column(String(15), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }


class Customer(User):
    __tablename__ = 'customer'
    
    @declared_attr
    def user_id(cls):
        return Column(String(10), ForeignKey('user.id'), primary_key=True)
    
    # 关系
    cars = relationship("Car", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    
    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }


class Worker(User):
    __tablename__ = 'worker'
    
    @declared_attr
    def user_id(cls):
        return Column(String(10), ForeignKey('user.id'), primary_key=True)
    
    worker_type = Column(Integer, ForeignKey('wage.worker_type'), nullable=False)
    
    # 关系
    logs = relationship("Log", back_populates="worker")
    wage = relationship("Wage", back_populates="workers")
    distributions = relationship("Distribute", back_populates="worker")
    
    __mapper_args__ = {
        'polymorphic_identity': 'worker',
    }


class Administrator(User):
    __tablename__ = 'administrator'
    
    @declared_attr
    def user_id(cls):
        return Column(String(10), ForeignKey('user.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'administrator',
    }
