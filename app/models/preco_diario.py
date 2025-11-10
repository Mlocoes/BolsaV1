"""
Modelo PrecoDiario - Precios de Cierre Diarios

Este módulo define el modelo para almacenar los precios de cierre diarios
de los activos financieros.
"""

from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class PrecoDiario(Base):
    """Modelo para precios de cierre diarios"""
    __tablename__ = "precos_diarios"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    data = Column(Date, nullable=False)
    preco_fechamento = Column(Numeric(12, 4), nullable=False)
    
    # Relaciones
    ativo = relationship("Ativo", back_populates="precos_diarios")