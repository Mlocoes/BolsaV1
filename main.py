"""
BolsaV1 - Sistema Integral de Gestión de Activos Financieros

Aplicación principal con sistema de autenticación integrado.

Autor: BolsaV1 Team
Versión: 3.0.0 - FASE 3 (Autenticación y Multi-usuario)
"""

import streamlit as st
import sys
import os

# Añadir el directorio raíz al path para imports
sys.path.append(os.path.dirname(__file__))

# Imports de la aplicación modular
from app.utils import setup_logging, get_logger, Config, init_database
from app.utils.auth import StreamlitAuth
from app.pages.layout import show_header, show_sidebar, show_footer
from app.pages.router import route_to_page
from app.models.base import remove_db_session
from app.pages.auth import show_login_page, show_register_page


def configure_streamlit():
    """Configura la aplicación Streamlit"""
    st.set_page_config(**Config.get_streamlit_config())


def initialize_application():
    """Inicializa los componentes básicos de la aplicación"""
    logger = setup_logging()
    logger.info(f"Iniciando {Config.APP_NAME} v{Config.APP_VERSION}")
    if not init_database():
        st.error("❌ Error al conectar con la base de datos")
        st.stop()
        return False
    logger.info("Aplicación inicializada correctamente")
    return True


def main():
    """Función principal de la aplicación"""
    configure_streamlit()
    if not initialize_application():
        return
    
    StreamlitAuth.initialize_session()
    logger = get_logger('main')
    logger.info("Iniciando aplicación - verificando autenticación")
    
    try:
        is_auth = StreamlitAuth.is_authenticated()
        logger.info(f"Estado de autenticación: {is_auth}")

        if not is_auth:
            logger.info("Mostrando página de login")
            if st.session_state.get("show_register", False):
                logger.info("Mostrando página de registro")
                show_register_page()
            else:
                logger.info("Mostrando página de login")
                show_login_page()
            return

        logger.info("Usuario autenticado, mostrando aplicación principal")
        show_header()
        selected_menu = show_sidebar()
        route_to_page(selected_menu)
        show_footer()
    finally:
        remove_db_session()


if __name__ == "__main__":
    main()
