"""
Modelo Ativo - Activos/Valores de Bolsa

Este módulo define el modelo para los activos financieros (acciones, ETFs, etc.)
que se pueden negociar en el sistema.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Ativo(Base):
    """Modelo para activos/valores de bolsa"""
    __tablename__ = "ativos"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, nullable=False)
    nome = Column(String(100))
    ativo = Column(Boolean, default=True)
    
    # Relaciones
    precos_diarios = relationship("PrecoDiario", back_populates="ativo")
    operacoes = relationship("Operacao", back_populates="ativo")
    posicoes = relationship("Posicao", back_populates="ativo")