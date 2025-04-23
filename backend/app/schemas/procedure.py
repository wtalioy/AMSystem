from typing import Optional
from pydantic import BaseModel


# Shared properties
class ProcedureBase(BaseModel):
    procedure_text: str
    order_id: str
    current_status: int = 0  # 0: pending, 1: in progress, 2: completed


# Properties to receive via API on creation
class ProcedureCreate(ProcedureBase):
    pass


# Properties to receive via API on update
class ProcedureUpdate(BaseModel):
    procedure_text: Optional[str] = None
    current_status: Optional[int] = None


# Properties shared by models stored in DB
class ProcedureInDBBase(ProcedureBase):
    procedure_id: int

    class Config:
        orm_mode = True


# Properties to return via API
class Procedure(ProcedureInDBBase):
    pass
