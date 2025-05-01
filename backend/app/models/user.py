from app.dbrm import Table, Column, String, TinyInt, Char

class User(Table):
    __tablename__ = 'User'
    
    id = Column(Char(10), primary_key=True)
    user_name = Column(String(10), nullable=False)
    user_pwd = Column(String(100), nullable=False)  # store hashed password
    user_type = Column(String(15), nullable=False, check="IN ('user', 'customer', 'worker', 'administrator')")


class Customer(Table):
    __tablename__ = 'Customer'
    
    user_id = Column(Char(10), primary_key=True, foreign_key="user.id", on_delete="SET NULL")


class Worker(Table):
    __tablename__ = 'Worker'
    
    user_id = Column(Char(10), primary_key=True, foreign_key="user.id", on_delete="SET NULL")
    worker_type = Column(TinyInt, foreign_key="Wage.worker_type", nullable=False)


class Administrator(Table):
    __tablename__ = 'Administrator'
    
    user_id = Column(Char(10), primary_key=True, foreign_key="user.id")