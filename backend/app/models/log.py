from app.dbrm import Table, Column, Char, Text, Timestamp, Decimal, Text, model_register

@model_register(dependencies=["ServiceOrder", "Worker"])
class Log(Table):
    __tablename__ = "ServiceLog"

    log_time = Column(Timestamp, nullable=False, primary_key=True)
    consumption = Column(Text, nullable=False)
    cost = Column(Decimal(10, 2), nullable=False)
    duration = Column(Decimal(3, 1), nullable=False)
    
    # Soft delete and audit fields
    created_at = Column(Timestamp, nullable=False, default='CURRENT_TIMESTAMP')
    updated_at = Column(Timestamp, nullable=False, default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    deleted_at = Column(Timestamp, nullable=True)  # NULL = not deleted
    created_by = Column(Char(10), nullable=True)
    updated_by = Column(Char(10), nullable=True)
    deleted_by = Column(Char(10), nullable=True)

    order_id = Column(Char(10), primary_key=True, foreign_key='ServiceOrder.order_id', nullable=False, on_delete="CASCADE", on_update="CASCADE", index=True)
    worker_id = Column(Char(10), foreign_key='Worker.user_id', nullable=False, on_delete="CASCADE", on_update="CASCADE", index=True)