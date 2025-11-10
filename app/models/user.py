"""
Modelo de Usuario para sistema de autenticación
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class User(Base):
    """
    Modelo de Usuario para autenticación y autorización
    
    Representa un usuario del sistema con capacidades de autenticación,
    autorización y gestión de cartera independiente.
    """
    __tablename__ = "users"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    
    # Estado y permisos
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Metadatos adicionales
    avatar_url = Column(String(255))
    bio = Column(Text)
    
    # Relaciones
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    ativos = relationship("Ativo", back_populates="user", cascade="all, delete-orphan")
    operacoes = relationship("Operacao", back_populates="user", cascade="all, delete-orphan")
    posicoes = relationship("Posicao", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """Convierte el usuario a diccionario (sin password)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "avatar_url": self.avatar_url,
            "bio": self.bio
        }
    
    @property
    def display_name(self):
        """Nombre para mostrar (full_name o username)"""
        return self.full_name or self.username
    
    @property
    def is_authenticated(self):
        """Para compatibilidad con sistemas de auth"""
        return self.is_active