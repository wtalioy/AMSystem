from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Numeric, text
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Log(Base):
    id = Column(String(10), primary_key=True, index=True)
    log_time = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    consumption = Column(Text, nullable=False)  # 材料消耗描述
    cost = Column(Numeric(10, 2), nullable=False)  # 材料成本
    duration = Column(Numeric(3, 1), nullable=False)  # 工作时长
    
    # 外键关系
    order_id = Column(String(10), ForeignKey('order.order_id'), nullable=False)
    worker_id = Column(String(10), ForeignKey('worker.user_id'), nullable=False)
    
    # 关系
    order = relationship("Order", back_populates="logs")
    worker = relationship("Worker", back_populates="logs")
