from app.dbrm.schema import TableBase, Column
from app.dbrm import String, Integer

class Car(TableBase):
    __tablename__ = "car"
    
    car_id = Column(String(10), primary_key=True, comment='车辆ID')
    car_type = Column(Integer, nullable=False, comment='车辆类型')
    customer_id = Column(String(10), foreign_key='customer.user_id', comment='客户ID')
    
    def get_customer(self, session):
        from app.dbrm.query import Select
        
        if not self.customer_id:
            return None
            
        query = Select().from_('customer').where(f"user_id = '{self.customer_id}'")
        session.execute(query)
        customer_data = session.fetch_as_dict()
        
        if not customer_data:
            return None
            
        from app.models.user import Customer
        return Customer._from_row(customer_data)
        
    def get_orders(self, session):
        from app.dbrm.query import Select
        
        query = Select().from_('order').where(f"car_id = '{self.car_id}'")
        session.execute(query)
        orders_data = session.fetchall_as_dict()
        
        if not orders_data:
            return []
            
        from app.models.order import Order
        return [Order._from_row(order_data) for order_data in orders_data]
