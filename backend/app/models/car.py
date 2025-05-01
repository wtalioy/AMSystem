from app.dbrm import Table, Column, Char, Integer

class Car(Table):
    __tablename__ = "Car"
    
    car_id = Column(Char(10), primary_key=True)
    car_type = Column(Integer, nullable=False, on_delete="SET NULL", on_update="CASCADE")
    
    customer_id = Column(Char(10), foreign_key='Customer.user_id')
    
    def get_customers(self, session):
        from app.models.user import Customer
        customers_data = session.query(Customer).filter_by(user_id=self.customer_id).all()
        if not customers_data:
            return []
        return customers_data
        
    def get_orders(self, session):
        from app.models.order import Order
        orders_data = session.query(Order).filter_by(car_id=self.car_id).all()
        if not orders_data:
            return []
        return orders_data