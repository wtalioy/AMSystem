from typing import List, Optional, Dict, Any
from datetime import datetime
from app.dbrm import Session, Condition
from app.crud.base import CRUDBase
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogUpdate
import random
import string


class CRUDAuditLog(CRUDBase[AuditLog, AuditLogCreate, AuditLogUpdate]):
    def create_audit_entry(
        self,
        db: Session,
        *,
        table_name: str,
        record_id: str,
        operation: str,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> AuditLog:
        """Create a new audit log entry"""
        # Generate unique audit ID
        audit_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Calculate changed fields if both old and new values provided
        changed_fields = None
        if old_values and new_values:
            changed_fields = [
                field for field, value in new_values.items()
                if field in old_values and old_values[field] != value
            ]
        
        audit_entry = AuditLog(
            audit_id=audit_id,
            table_name=table_name,
            record_id=record_id,
            operation=operation.upper(),
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            user_id=user_id
        )
        
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
    
    def get_audit_trail_for_record(
        self, db: Session, record_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail for a specific record"""
        return db.query(AuditLog).filter_by(
            record_id=record_id
        ).order_by_desc(AuditLog.timestamp).offset(skip).limit(limit).all()
    

    
    def get_recent_changes(
        self, db: Session, hours: int = 24, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get recent changes within specified hours"""
        from datetime import timedelta
        since = datetime.now() - timedelta(hours=hours)
        
        return db.query(AuditLog).where(
            Condition.gte(AuditLog.timestamp, since)
        ).order_by_desc(AuditLog.timestamp).offset(skip).limit(limit).all()
    
    
    def rollback_to_version(
        self, db: Session, target_audit_id: str
    ) -> Optional[Dict]:
        """
        Get the state of a record at a specific audit point for rollback
        Returns the old_values from the target audit entry
        """
        audit_entry = db.query(AuditLog).filter_by(
            audit_id=target_audit_id
        ).first()
        
        if audit_entry and audit_entry.old_values:
            return {
                "record_id": audit_entry.record_id,
                "table_name": audit_entry.table_name,
                "old_values": audit_entry.old_values,
                "operation": audit_entry.operation,
                "timestamp": audit_entry.timestamp.isoformat() if audit_entry.timestamp else None
            }
        return None
    
    def get_change_summary(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get summary of changes in a date range"""
        changes = db.query(AuditLog).where(
            Condition.gte(AuditLog.timestamp, start_date),
            Condition.lte(AuditLog.timestamp, end_date)
        ).all()
        
        summary = {
            "total_changes": len(changes),
            "by_table": {},
            "by_operation": {},
            "by_user": {}
        }
        
        for change in changes:
            # By table
            if change.table_name not in summary["by_table"]:
                summary["by_table"][change.table_name] = 0
            summary["by_table"][change.table_name] += 1
            
            # By operation
            if change.operation not in summary["by_operation"]:
                summary["by_operation"][change.operation] = 0
            summary["by_operation"][change.operation] += 1
            
            # By user
            user_id = change.user_id or "system"
            if user_id not in summary["by_user"]:
                summary["by_user"][user_id] = 0
            summary["by_user"][user_id] += 1
        
        return summary


audit_log = CRUDAuditLog(AuditLog) 