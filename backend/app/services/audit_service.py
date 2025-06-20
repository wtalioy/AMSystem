"""
Core Audit Service

Simplified service focused only on audit trail management and data operations.
Decorator logic has been moved to app.core.audit_decorators for better separation of concerns.
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.dbrm import Session
from app.crud.crud_audit_log import audit_log
from app.schemas.audit_log import ChangeTrackingContext, AuditLogSummary, AuditLog


class AuditService:
    """Core audit service for audit trail management"""
    
    @staticmethod
    def _get_record_for_audit(db: Session, table_name: str, record_id: str):
        """Get a record for audit logging purposes"""
        try:
            from app.crud import order, user, car
            
            if table_name == "ServiceOrder":
                return order.get_by_order_id(db, order_id=record_id)
            elif table_name in ["User", "Customer", "Worker", "Administrator"]:
                return user.get_by_id(db, user_id=record_id)
            elif table_name == "Car":
                return car.get_by_car_id(db, car_id=record_id)
            # Add more mappings as needed
            
        except Exception:
            return None
        return None
    
    @staticmethod
    def serialize_for_audit(model_instance) -> Dict[str, Any]:
        """Serialize a model instance for audit logging"""
        if not model_instance:
            return {}
        
        # For Pydantic models, use model_dump with JSON mode for proper serialization
        if hasattr(model_instance, 'model_dump'):
            return model_instance.model_dump(mode='json')
        
        # For database models (fallback for CRUD operations)
        result = {}
        for column in model_instance.__table__.columns:
            value = getattr(model_instance, column.name, None)
            # Convert datetime objects to ISO string for JSON serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            # Convert Decimal to float for JSON serialization
            elif hasattr(value, '__float__'):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = str(value)
            result[column.name] = value
        
        return result
    
    @staticmethod
    def log_change(
        db: Session,
        table_name: str,
        record_id: str,
        operation: str,
        old_data: Optional[Dict] = None,
        new_data: Optional[Dict] = None,
        context: Optional[ChangeTrackingContext] = None
    ) -> AuditLog:
        """Log a change to the audit trail"""
        audit_entry = audit_log.create_audit_entry(
            db,
            table_name=table_name,
            record_id=record_id,
            operation=operation,
            old_values=old_data,
            new_values=new_data,
            user_id=context.user_id if context else None
        )
        return audit_entry
    
    @staticmethod
    def get_audit_trail(
        db: Session, record_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail for a specific record"""
        audit_entries = audit_log.get_audit_trail_for_record(db, record_id, skip, limit)
        return audit_entries
    
    @staticmethod
    def get_change_summary(
        db: Session, start_date: datetime, end_date: datetime
    ) -> AuditLogSummary:
        """Get summary of changes in a date range"""
        summary_data = audit_log.get_change_summary(db, start_date, end_date)
        return summary_data
    
    @staticmethod
    def rollback_to_version(
        db: Session, target_audit_id: str
    ) -> Optional[AuditLog]:
        """Get rollback data for a record at a specific audit point"""
        return audit_log.rollback_to_version(db, target_audit_id)
    
    @staticmethod
    def get_recent_changes(
        db: Session, hours: int = 24, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get recent changes within specified hours"""
        audit_entries = audit_log.get_recent_changes(db, hours, skip, limit)
        return audit_entries