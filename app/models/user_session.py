"""
Modelo de Sesión de Usuario para gestión de autenticación
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INET
from app.models.base import Base


class UserSession(Base):
    """
    Modelo de Sesión de Usuario
    
    Gestiona las sesiones activas de usuarios para control de acceso
    y seguridad. Permite logout desde múltiples dispositivos y 
    tracking de actividad.
    """
    __tablename__ = "user_sessions"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Expiración y timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Metadatos de sesión
    ip_address = Column(INET)
    user_agent = Column(Text)
    device_info = Column(String(200))
    
    # Estado de la sesión
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True))
    revoked_reason = Column(String(100))
    
    # Relaciones
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
    
    def to_dict(self):
        """Convierte la sesión a diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "device_info": self.device_info,
            "is_revoked": self.is_revoked,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None
        }
    
    @property
    def is_expired(self):
        """Verifica si la sesión ha expirado"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_valid(self):
        """Verifica si la sesión es válida (no expirada ni revocada)"""
        return not self.is_expired and not self.is_revoked
    
    def revoke(self, reason="user_logout"):
        """Revoca la sesión"""
        from datetime import datetime, timezone
        self.is_revoked = True
        self.revoked_at = datetime.now(timezone.utc)
        self.revoked_reason = reason
    
    def extend_expiry(self, hours=24):
        """Extiende la expiración de la sesión"""
        from datetime import datetime, timezone, timedelta
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        
    def update_activity(self):
        """Actualiza el timestamp de última actividad"""
        from datetime import datetime, timezone
        self.last_activity = datetime.now(timezone.utc)