"""
BolsaV1 - Sistema Integral de Gestión de Activos Financieros

Aplicación principal refactorizada con arquitectura modular.

Autor: BolsaV1 Team
Versión: 2.0.0
"""

import streamlit as st
import sys
import os

# Añadir el directorio raíz al path para imports
sys.path.append(os.path.dirname(__file__))

# Imports de la aplicación modular
from app.utils import setup_logging, get_logger, Config, init_database
from app.pages import (
    show_valores_page,
    show_cotizaciones_page,
    show_operaciones_page,
    show_posiciones_page,
    show_historico_page
)


def configure_streamlit():
    """Configura la aplicación Streamlit"""
    st.set_page_config(**Config.get_streamlit_config())


def show_header():
    """Muestra el header principal de la aplicación"""
    st.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
    st.subheader(Config.APP_DESCRIPTION)


def show_sidebar():
    """Configura y muestra la barra lateral con navegación"""
    st.sidebar.title("🧭 Navegación")
    
    # Información del sistema
    st.sidebar.markdown(f"**Versión:** {Config.APP_VERSION}")
    
    # Selector de página principal
    menu = st.sidebar.selectbox(
        "Seleccionar Página",
        [
            "Valores",
            "Cotizaciones", 
            "Operaciones",
            "Posiciones",
            "Histórico"
        ],
        index=0
    )
    
    # Información adicional en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    st.sidebar.info("""
    **BolsaV1** es un sistema integral para gestionar activos financieros.
    
    **Características:**
    - 📊 Cotizaciones en tiempo real
    - 💼 Gestión de operaciones
    - 📈 Análisis de posiciones
    - 📋 Histórico completo
    """)
    
    return menu


def initialize_application():
    """Inicializa los componentes básicos de la aplicación"""
    # Configurar logging
    logger = setup_logging()
    logger.info(f"Iniciando {Config.APP_NAME} v{Config.APP_VERSION}")
    
    # Inicializar base de datos
    if not init_database():
        st.error("❌ Error al conectar con la base de datos")
        st.stop()
        return False
    
    logger.info("Aplicación inicializada correctamente")
    return True


def route_to_page(menu_selection: str):
    """
    Rutea a la página seleccionada
    
    Args:
        menu_selection: Página seleccionada en el menú
    """
    logger = get_logger('main')
    
    try:
        if menu_selection == "Valores":
            show_valores_page()
        elif menu_selection == "Cotizaciones":
            show_cotizaciones_page()
        elif menu_selection == "Operaciones":
            show_operaciones_page()
        elif menu_selection == "Posiciones":
            show_posiciones_page()
        elif menu_selection == "Histórico":
            show_historico_page()
        else:
            st.error(f"❌ Página no encontrada: {menu_selection}")
            
    except Exception as e:
        logger.error(f"Error en página {menu_selection}: {e}", exc_info=True)
        st.error(f"❌ Error al cargar la página: {e}")
        
        # Mostrar información de debugging en modo desarrollo
        if Config.LOG_LEVEL == "DEBUG":
            with st.expander("🔍 Información de Debug"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())


def show_footer():
    """Muestra el footer de la aplicación"""
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("🔄 **Estado del Sistema**: ✅ Funcionando")
    
    with col2:
        st.markdown(f"🗂️ **Base de Datos**: PostgreSQL")
    
    with col3:
        st.markdown(f"📊 **API**: Yahoo Finance")
    
    # Copyright
    st.markdown(
        "<div style='text-align: center; color: gray; padding: 10px;'>"
        f"© 2024 {Config.APP_NAME} v{Config.APP_VERSION} - Sistema de Gestión de Activos Financieros"
        "</div>",
        unsafe_allow_html=True
    )


def main():
    """Función principal de la aplicación"""
    # Configurar Streamlit
    configure_streamlit()
    
    # Inicializar aplicación
    if not initialize_application():
        return
    
    # Mostrar header
    show_header()
    
    # Configurar sidebar y obtener selección de menú
    selected_menu = show_sidebar()
    
    # Rutear a la página correspondiente
    route_to_page(selected_menu)
    
    # Mostrar footer
    show_footer()


if __name__ == "__main__":
    main()