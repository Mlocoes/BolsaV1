"""
BolsaV1 - Módulo Principal de la Aplicación

Sistema Integral de Gestión de Activos Financieros
Arquitectura Modular v2.0.0

Este módulo organiza todos los componentes de la aplicación:
- models: Modelos SQLAlchemy de base de datos
- services: Lógica de negocio y servicios
- pages: Páginas de interfaz de usuario
- utils: Utilidades y configuraciones

Autor: BolsaV1 Team
Fecha: 2024
Versión: 2.0.0
"""

__version__ = "2.0.0"
__description__ = "Sistema Integral de Gestión de Activos Financieros"

# Importaciones principales para facilitar el uso
from .models import Base, SessionLocal, get_db
from .utils import Config, setup_logging
from .services import AtivoService, CotacaoService, OperacaoService, PosicaoService

# Metadatos del módulo
__all__ = [
    'Base',
    'SessionLocal', 
    'get_db',
    'Config',
    'setup_logging',
    'AtivoService',
    'CotacaoService',
    'OperacaoService',
    'PosicaoService'
]