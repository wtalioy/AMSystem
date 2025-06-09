from app.dbrm import Table, Column, String, TinyInt, Char, Timestamp, Integer, model_register
from app.core.enum import WorkerAvailabilityStatus

@model_register
class User(Table):
    __tablename__ = 'User'
    
    user_id = Column(Char(10), nullable=False, primary_key=True)
    user_name = Column(String(10), nullable=False)
    user_pwd = Column(String(100), nullable=False)  # store hashed password
    user_type = Column(String(15), nullable=False, check="IN ('user', 'customer', 'worker', 'administrator')")
    
    # Soft delete and audit fields
    created_at = Column(Timestamp, nullable=False, default='CURRENT_TIMESTAMP')
    updated_at = Column(Timestamp, nullable=False, default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    deleted_at = Column(Timestamp, nullable=True)  # NULL = not deleted
    created_by = Column(Char(10), nullable=True)
    updated_by = Column(Char(10), nullable=True)
    deleted_by = Column(Char(10), nullable=True)

@model_register(dependencies=["User"])
class Customer(Table):
    __tablename__ = 'Customer'

    user_id = Column(Char(10), nullable=False, primary_key=True, foreign_key="User.user_id")

@model_register(dependencies=["User", "Wage"])
class Worker(Table):
    __tablename__ = 'Worker'

    user_id = Column(Char(10), nullable=False, primary_key=True, foreign_key="User.user_id")
    worker_type = Column(TinyInt, foreign_key="Wage.worker_type", nullable=False)
    
    availability_status = Column(Integer, nullable=False, default=WorkerAvailabilityStatus.AVAILABLE)


@model_register(dependencies=["User"])
class Administrator(Table):
    __tablename__ = 'Administrator'

    user_id = Column(Char(10), nullable=False, primary_key=True, foreign_key="User.user_id")