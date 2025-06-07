from app.dbrm import Table, Column, Char, TinyText, Integer, model_register
from app.core.enum import ProcedureStatus

@model_register(dependencies=["ServiceOrder"])
class ServiceProcedure(Table):
    __tablename__ = "ServiceProcedure"

    procedure_id = Column(Integer, nullable=False, primary_key=True)
    procedure_text = Column(TinyText, nullable=False)
    current_status = Column(Integer, nullable=False, default=ProcedureStatus.PENDING)

    order_id = Column(Char(10), primary_key=True, foreign_key='ServiceOrder.order_id', on_delete="CASCADE", on_update="CASCADE")
