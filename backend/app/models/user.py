from app.dbrm import Table, Column, String, VarChar, Char, Integer, model_register
from app.core.enum import WorkerAvailabilityStatus

@model_register
class User(Table):
    __tablename__ = 'User'
    
    user_id = Column(Char(10), nullable=False, primary_key=True)
    user_name = Column(String(10), nullable=False)
    user_pwd = Column(String(100), nullable=False)  # store hashed password
    user_type = Column(String(15), nullable=False, check="IN ('user', 'customer', 'worker', 'administrator')")
    

@model_register(dependencies=["User"])
class Customer(Table):
    __tablename__ = 'Customer'

    user_id = Column(Char(10), nullable=False, primary_key=True, foreign_key="User.user_id", on_delete="CASCADE")


@model_register(dependencies=["User", "Wage"])
class Worker(Table):
    __tablename__ = 'Worker'

    user_id = Column(Char(10), nullable=False, primary_key=True, foreign_key="User.user_id", on_delete="CASCADE")
    worker_type = Column(VarChar(20), foreign_key="Wage.worker_type", nullable=False)
    
    availability_status = Column(Integer, nullable=False, default=WorkerAvailabilityStatus.AVAILABLE)


@model_register(dependencies=["User"])
class Administrator(Table):
    __tablename__ = 'Administrator'

    user_id = Column(Char(10), nullable=False, primary_key=True, foreign_key="User.user_id", on_delete="CASCADE")