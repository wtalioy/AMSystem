from pydantic import BaseModel


class ProcedureBase(BaseModel):
    order_id: str


class ProcedureCreate(ProcedureBase):
    procedure_text: str


class ProcedureUpdate(ProcedureBase):
    procedure_id: int
    current_status: int


class ProcedureInDBBase(ProcedureBase):
    procedure_id: int
    procedure_text: str
    current_status: int

    class Config:
        from_attributes = True


class Procedure(ProcedureInDBBase):
    pass
