"""
Modelo Operacao - Operaciones de Compra/Venta

Este módulo define el modelo para las operaciones de compra y venta
de activos financieros.
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Operacao(Base):
    """Modelo para operaciones de compra/venta"""
    __tablename__ = "operacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    data = Column(Date, nullable=False)
    tipo = Column(String(10), CheckConstraint("tipo IN ('compra','venda')"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco = Column(Numeric(12, 4), nullable=False)
    
    # Relaciones
    ativo = relationship("Ativo", back_populates="operacoes")