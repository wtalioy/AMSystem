from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Wage(Base):
    worker_type = Column(Integer, primary_key=True)
    wage_per_hour = Column(Integer, nullable=False)
    
    # 关系
    workers = relationship("Worker", back_populates="wage")
