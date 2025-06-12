from app.dbrm import Table, Column, Char, model_register, VarChar

@model_register(dependencies=["Customer", "CarType"])
class Car(Table):
    __tablename__ = "Car"
    
    car_id = Column(Char(10), nullable=False, primary_key=True)
    
    car_type = Column(VarChar(20), nullable=False, foreign_key='CarType.car_type')
    customer_id = Column(Char(10), foreign_key='Customer.user_id')

@model_register
class CarType(Table):
    __tablename__ = "CarType"

    car_type = Column(VarChar(20), nullable=False, primary_key=True)