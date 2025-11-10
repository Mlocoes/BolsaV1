"""
Modelo Posicao - Posiciones Consolidadas

Este módulo define el modelo para las posiciones consolidadas de activos,
incluyendo cantidades, precios medios y resultados.
"""

from sqlalchemy import Column, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Posicao(Base):
    """Modelo para posiciones consolidadas"""
    __tablename__ = "posicoes"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    quantidade_total = Column(Integer, default=0)
    preco_medio = Column(Numeric(12, 4), default=0)
    preco_atual = Column(Numeric(12, 4), default=0)
    resultado_dia = Column(Numeric(12, 4), default=0)
    resultado_acumulado = Column(Numeric(12, 4), default=0)
    
    # Multi-tenancy: Cada posición pertenece a un usuario
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relaciones
    user = relationship("User", back_populates="posicoes")
    ativo = relationship("Ativo", back_populates="posicoes")
    
    # Una posición única por activo por usuario
    __table_args__ = (
        UniqueConstraint('ativo_id', 'user_id', name='unique_position_per_user'),
    )