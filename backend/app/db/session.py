from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建SQLAlchemy引擎
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# 创建SessionLocal类，每个实例将是一个数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，所有模型将继承这个类
Base = declarative_base()
