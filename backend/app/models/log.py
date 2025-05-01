from app.dbrm import Table, Column, Char, Text, Timestamp, Decimal, Text

class Log(Table):
    __tablename__ = "Log"

    log_time = Column(Timestamp, primary_key=True)
    consumption = Column(Text, nullable=False)
    cost = Column(Decimal(10, 2), nullable=False)
    duration = Column(Decimal(3, 1), nullable=False)

    order_id = Column(Char(10), primary_key=True, foreign_key='Order.order_id', nullable=False)
    worker_id = Column(Char(10), foreign_key='Worker.user_id', nullable=False)