from app.dbrm import Table, Column, Char, TinyText, Integer

class Procedure(Table):
    __tablename__ = "Procedure"

    procedure_id = Column(Integer, primary_key=True, autoincrement=True)
    procedure_text = Column(TinyText, nullable=False)
    current_status = Column(Integer, nullable=False, default=1)  # 1: ongoing, 2: finished
    
    order_id = Column(Char(10), primary_key=True, foreign_key='Order.order_id')
