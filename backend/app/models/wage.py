from app.dbrm import Table, Column, TinyInt, Integer, model_register

@model_register
class Wage(Table):
    __tablename__ = 'Wage'
    
    worker_type = Column(TinyInt, primary_key=True, autoincrement=True, on_delete="SET NULL", on_update="CASCADE")
    wage_per_hour = Column(Integer, nullable=False)