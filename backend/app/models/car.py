from app.dbrm import Table, Column, Char, Integer, model_register

@model_register(dependencies=["Customer"])
class Car(Table):
    __tablename__ = "Car"
    
    car_id = Column(Char(10), primary_key=True)
    car_type = Column(Integer, nullable=False, on_delete="SET NULL", on_update="CASCADE")
    
    customer_id = Column(Char(10), foreign_key='Customer.user_id')