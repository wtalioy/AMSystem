from app.dbrm import Table, Column, Char, Timestamp, JSON, model_register

@model_register
class AuditLog(Table):
    __tablename__ = "AuditLog"
    
    audit_id = Column(Char(10), nullable=False, primary_key=True)
    table_name = Column(Char(50), nullable=False)          # Which table was changed
    record_id = Column(Char(10), nullable=False)           # ID of the changed record
    operation = Column(Char(10), nullable=False)           # INSERT, UPDATE, DELETE
    old_values = Column(JSON, nullable=True)               # Previous state (NULL for INSERT)
    new_values = Column(JSON, nullable=True)               # New state (NULL for DELETE)
    changed_fields = Column(JSON, nullable=True)           # List of field names that changed
    timestamp = Column(Timestamp, nullable=False, default='CURRENT_TIMESTAMP')
    user_id = Column(Char(10), nullable=True)              # Who made the change 