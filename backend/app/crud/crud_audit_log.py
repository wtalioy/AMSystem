from typing import List, Optional, Dict, Any
from datetime import datetime
from app.dbrm import Session, Condition

from app.models import AuditLog as AuditLogModel
from app.schemas import AuditLog, AuditLogSummary
import random
import string
import json


class CRUDAuditLog:
    def create_audit_entry(
        self,
        db: Session,
        *,
        table_name: str,
        record_id: str,
        operation: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
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
        
        audit_entry = AuditLogModel(
            audit_id=audit_id,
            table_name=table_name,
            record_id=record_id,
            operation=operation.upper(),
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            changed_fields=changed_fields,
            user_id=user_id
        )
        
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)

        audit_entry.old_values = json.loads(audit_entry.old_values) if audit_entry.old_values else None
        audit_entry.new_values = json.loads(audit_entry.new_values) if audit_entry.new_values else None
        return AuditLog.model_validate(audit_entry)
    
    def get_audit_trail_for_record(
        self, db: Session, record_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail for a specific record"""
        objs = db.query(AuditLogModel).filter_by(
            record_id=record_id
        ).order_by_desc(AuditLogModel.timestamp).offset(skip).limit(limit).all()
        
        if not objs:
            return []
        return [AuditLog.model_validate(obj) for obj in objs]

    def get_recent_changes(
        self, db: Session, hours: int = 24, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get recent changes within specified hours"""
        from datetime import timedelta
        since = datetime.now() - timedelta(hours=hours)
        
        objs = db.query(AuditLogModel).where(
            Condition.gte(AuditLogModel.timestamp, since)
        ).order_by_desc(AuditLogModel.timestamp).offset(skip).limit(limit).all()
        
        if not objs:
            return []
        for obj in objs:
            obj.old_values = json.loads(obj.old_values) if obj.old_values else None
            obj.new_values = json.loads(obj.new_values) if obj.new_values else None
        return [AuditLog.model_validate(obj) for obj in objs]
    
    
    def rollback_to_version(
        self, db: Session, target_audit_id: str
    ) -> Optional[AuditLog]:
        """
        Get the state of a record at a specific audit point for rollback
        Returns the old_values from the target audit entry
        """
        obj = db.query(AuditLogModel).filter_by(
            audit_id=target_audit_id
        ).first()
        
        if obj and obj.old_values:
            obj.old_values = json.loads(obj.old_values) if obj.old_values else None
            obj.new_values = json.loads(obj.new_values) if obj.new_values else None
            return AuditLog.model_validate(obj)
        return None
    
    def get_change_summary(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> AuditLogSummary:
        """Get summary of changes in a date range"""
        objs = db.query(AuditLogModel).where(
            Condition.gte(AuditLogModel.timestamp, start_date),
            Condition.lte(AuditLogModel.timestamp, end_date)
        ).all()
        
        summary = {
            "total_changes": len(objs),
            "by_table": {},
            "by_operation": {},
            "by_user": {}
        }
        
        for obj in objs:
            # By table
            if obj.table_name not in summary["by_table"]:
                summary["by_table"][obj.table_name] = 0
            summary["by_table"][obj.table_name] += 1
            
            # By operation
            if obj.operation not in summary["by_operation"]:
                summary["by_operation"][obj.operation] = 0
            summary["by_operation"][obj.operation] += 1
            
            # By user
            user_id = obj.user_id or "system"
            if user_id not in summary["by_user"]:
                summary["by_user"][user_id] = 0
            summary["by_user"][user_id] += 1
        
        return AuditLogSummary(**summary)


audit_log = CRUDAuditLog() 