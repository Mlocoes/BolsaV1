"""
Modelo Posicao - Posiciones Consolidadas

Este módulo define el modelo para las posiciones consolidadas de activos,
incluyendo cantidades, precios medios y resultados.
"""

from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Posicao(Base):
    """Modelo para posiciones consolidadas"""
    __tablename__ = "posicoes"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), unique=True, nullable=False)
    quantidade_total = Column(Integer, default=0)
    preco_medio = Column(Numeric(12, 4), default=0)
    preco_atual = Column(Numeric(12, 4), default=0)
    resultado_dia = Column(Numeric(12, 4), default=0)
    resultado_acumulado = Column(Numeric(12, 4), default=0)
    
    # Relaciones
    ativo = relationship("Ativo", back_populates="posicoes")