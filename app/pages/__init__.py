"""
Módulo de Páginas de UI

Este módulo contiene todas las páginas de interfaz de usuario para BolsaV1.
"""

from .valores import show_valores_page
from .cotizaciones import show_cotizaciones_page
from .operaciones import show_operaciones_page
from .posiciones import show_posiciones_page
from .historico import show_historico_page

# Exportar todas las páginas
__all__ = [
    'show_valores_page',
    'show_cotizaciones_page',
    'show_operaciones_page',
    'show_posiciones_page',
    'show_historico_page'
]