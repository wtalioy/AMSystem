from app.dbrm import Table, Column, Char, Text, Timestamp, Decimal, Text, model_register

@model_register(dependencies=["ServiceOrder", "Worker"])
class Log(Table):
    __tablename__ = "ServiceLog"

    log_time = Column(Timestamp, nullable=False, primary_key=True)
    consumption = Column(Text, nullable=False)
    cost = Column(Decimal(10, 2), nullable=False)
    duration = Column(Decimal(3, 1), nullable=False)

    order_id = Column(Char(10), primary_key=True, foreign_key='ServiceOrder.order_id', nullable=False, on_delete="CASCADE", on_update="CASCADE", index=True)
    worker_id = Column(Char(10), foreign_key='Worker.user_id', nullable=False, on_delete="CASCADE", on_update="CASCADE", index=True)