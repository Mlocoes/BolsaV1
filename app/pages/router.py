"""
Módulo de Routing - FASE 3

Este módulo contiene la lógica para enrutar a las diferentes páginas
de la aplicación.
"""

import streamlit as st
from ..utils.auth import StreamlitAuth
from ..utils.config import Config
from ..utils.logging_config import get_logger

# Imports de páginas principales
from . import (
    show_valores_page,
    show_cotizaciones_page,
    show_operaciones_page,
    show_posiciones_page,
    show_historico_page
)

# Imports de páginas de autenticación
from .auth import show_login_page, show_register_page
from .profile import show_profile_page
from .admin import show_admin_page


def route_to_page(menu_selection: str):
    """
    Rutea a la página seleccionada

    Args:
        menu_selection: Página seleccionada en el menú
    """
    logger = get_logger('main')

    try:
        if menu_selection == "🔑 Iniciar Sesión":
            show_login_page()
            return
        elif menu_selection == "📝 Registrarse":
            show_register_page()
            return

        if not StreamlitAuth.is_authenticated():
            st.warning("🔐 Debes iniciar sesión para acceder a esta página")
            show_login_page()
            return

        if menu_selection == "📊 Valores":
            show_valores_page()
        elif menu_selection == "📈 Cotizaciones":
            show_cotizaciones_page()
        elif menu_selection == "💼 Operaciones":
            show_operaciones_page()
        elif menu_selection == "📋 Posiciones":
            show_posiciones_page()
        elif menu_selection == "📜 Histórico":
            show_historico_page()
        elif menu_selection == "👤 Perfil":
            show_profile_page()
        elif menu_selection == "👑 Administración":
            show_admin_page()
        else:
            st.error(f"❌ Página no encontrada: {menu_selection}")

    except Exception as e:
        logger.error(f"Error en página {menu_selection}: {e}", exc_info=True)
        st.error(f"❌ Error al cargar la página: {e}")

        if Config.LOG_LEVEL == "DEBUG":
            with st.expander("🔍 Información de Debug"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
