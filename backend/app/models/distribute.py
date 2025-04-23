from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric, text
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Distribute(Base):
    distribute_id = Column(Integer, primary_key=True, autoincrement=True)
    distribute_time = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    amount = Column(Numeric(10, 1), nullable=False)
    worker_id = Column(String(10), ForeignKey('worker.user_id'), nullable=False)
    
    # 关系
    worker = relationship("Worker", back_populates="distributions")
