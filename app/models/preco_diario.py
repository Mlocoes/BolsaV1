"""
Modelo PrecoDiario - Precios de Cierre Diarios

Este módulo define el modelo para almacenar los precios de cierre diarios
de los activos financieros.
"""

from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class PrecoDiario(Base):
    """Modelo para precios de cierre diarios"""
    __tablename__ = "precos_diarios"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    data = Column(Date, nullable=False)
    preco_fechamento = Column(Numeric(12, 4), nullable=False)
    
    # Multi-tenancy: Los precios pueden ser compartidos entre usuarios o específicos
    # Para optimización, los precios pueden ser globales pero filtrados por contexto de usuario
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Relaciones
    ativo = relationship("Ativo", back_populates="precos_diarios")
    
    # Un precio único por activo por fecha (puede ser global o por usuario)
    __table_args__ = (
        UniqueConstraint('ativo_id', 'data', 'user_id', name='unique_price_per_asset_date_user'),
    )