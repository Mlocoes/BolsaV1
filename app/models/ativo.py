"""
Modelo Ativo - Activos/Valores de Bolsa

Este módulo define el modelo para los activos financieros (acciones, ETFs, etc.)
que se pueden negociar en el sistema.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Ativo(Base):
    """Modelo para activos/valores de bolsa"""
    __tablename__ = "ativos"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False)
    nome = Column(String(100))
    ativo = Column(Boolean, default=True)
    
    # Multi-tenancy: Cada activo pertenece a un usuario
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relaciones
    user = relationship("User", back_populates="ativos")
    precos_diarios = relationship("PrecoDiario", back_populates="ativo")
    operacoes = relationship("Operacao", back_populates="ativo")
    posicoes = relationship("Posicao", back_populates="ativo")
    
    # Constraint único por usuario (permitir mismo ticker para usuarios diferentes)
    __table_args__ = (
        UniqueConstraint('ticker', 'user_id', name='unique_ticker_per_user'),
    )