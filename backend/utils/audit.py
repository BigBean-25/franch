from models import AuditLog
from datetime import datetime, timezone

async def log_audit(db, user_id: str, user_email: str, action: str, module: str, details: str = None, ip_address: str = None):
    """
    Create audit log entry
    """
    audit = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        module=module,
        details=details,
        ip_address=ip_address
    )
    
    doc = audit.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.audit_logs.insert_one(doc)
    return audit
