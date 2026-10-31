"""Admin Activity and Audit Log database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class AdminAuditLog(Base):
    """Audit log tracking administrative actions, access events, and data exports."""

    __tablename__ = "admin_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    admin_name = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False, index=True)  # LOGIN, VIEW_FARMERS, EXPORT_DATA, TOGGLE_STATUS, BACKUP_DB, RESTORE_DB, VIEW_ANALYTICS
    resource_type = Column(String(50), nullable=False, index=True)  # farmer, crop, expense, harvest, activity, backup, system
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)  # JSON-encoded parameters, record counts, filters
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    admin = relationship("User", back_populates="admin_logs")

    def __repr__(self):
        return f"<AdminAuditLog {self.id} {self.action} by {self.admin_name}>"
