from dbrm import Table, Column, Integer, Char, Timestamp, Decimal

class Distribute(Table):
    __tablename__ = "Distribute"
    
    distribute_id = Column(Integer, primary_key=True, autoincrement=True)
    distribute_time = Column(Timestamp, nullable=False)
    amount = Column(Decimal(10, 1), nullable=False)

    worker_id = Column(Char(10), foreign_key='Worker.worker_id', nullable=False)
    