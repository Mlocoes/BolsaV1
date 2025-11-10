"""
Módulo de Páginas de UI - FASE 3

Este módulo contiene todas las páginas de interfaz de usuario para BolsaV1,
incluyendo las nuevas páginas de autenticación y gestión de usuarios.
"""

# Páginas principales (requieren autenticación)
from .valores import show_valores_page
from .cotizaciones import show_cotizaciones_page
from .operaciones import show_operaciones_page
from .posiciones import show_posiciones_page
from .historico import show_historico_page

# Páginas de autenticación y gestión
from .auth import show_login_page, show_register_page
from .profile import show_profile_page
from .admin import show_admin_page

# Exportar todas las páginas
__all__ = [
    # Páginas principales
    'show_valores_page',
    'show_cotizaciones_page',
    'show_operaciones_page',
    'show_posiciones_page',
    'show_historico_page',
    
    # Páginas de autenticación
    'show_login_page',
    'show_register_page',
    
    # Páginas de gestión
    'show_profile_page',
    'show_admin_page'
]