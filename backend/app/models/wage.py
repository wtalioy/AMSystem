from app.dbrm import Table, Column, VarChar, Integer, model_register

@model_register
class Wage(Table):
    __tablename__ = 'Wage'
    
    worker_type = Column(VarChar(20), nullable=False, primary_key=True)
    wage_per_hour = Column(Integer, nullable=False)