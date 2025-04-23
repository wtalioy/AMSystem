from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Procedure(Base):
    procedure_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(10), ForeignKey('order.order_id'), nullable=False)
    procedure_text = Column(Text, nullable=False)
    current_status = Column(Integer, nullable=False, default=0)  # 0: 待处理, 1: 进行中, 2: 已完成
    
    # 关系
    order = relationship("Order", back_populates="procedures")
