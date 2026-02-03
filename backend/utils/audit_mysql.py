from sqlalchemy.ext.asyncio import AsyncSession
from sql_models import AuditLog
from datetime import datetime, timezone

async def log_audit_mysql(
    db: AsyncSession,
    user_id: str,
    user_email: str,
    action: str,
    resource_type: str,
    details: str,
    resource_id: str = None,
    ip_address: str = None,
    user_agent: str = None
):
    """Log audit entry to MySQL database"""
    
    audit_log = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(audit_log)
    await db.commit()
    return audit_log
