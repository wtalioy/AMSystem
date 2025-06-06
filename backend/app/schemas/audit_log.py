from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    table_name: str = Field(..., description="Name of the table that was modified")
    record_id: str = Field(..., description="ID of the record that was modified")
    operation: str = Field(..., description="Type of operation: INSERT, UPDATE, DELETE")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values (NULL for INSERT)")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values (NULL for DELETE)")
    changed_fields: Optional[List[str]] = Field(None, description="List of fields that changed")
    user_id: Optional[str] = Field(None, description="ID of user who made the change")


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(AuditLogBase):
    table_name: Optional[str] = None
    record_id: Optional[str] = None
    operation: Optional[str] = None


class AuditLog(AuditLogBase):
    audit_id: str = Field(..., description="Unique audit log entry ID")
    timestamp: datetime = Field(..., description="When the change occurred")
    
    class Config:
        from_attributes = True


class AuditLogSummary(BaseModel):
    """Summary of audit log activity"""
    total_changes: int
    by_table: Dict[str, int]
    by_operation: Dict[str, int]
    by_user: Dict[str, int]


class RollbackRequest(BaseModel):
    """Request to rollback to a specific audit point"""
    target_audit_id: str


class ChangeTrackingContext(BaseModel):
    """Context information for change tracking"""
    user_id: Optional[str] = None 