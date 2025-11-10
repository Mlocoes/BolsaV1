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

# Imports de páginas principales
from app.pages import (
    show_valores_page,
    show_cotizaciones_page,
    show_operaciones_page,
    show_posiciones_page,
    show_historico_page
)

# Imports de páginas de autenticación
from app.pages.auth import show_login_page, show_register_page
from app.pages.profile import show_profile_page
from app.pages.admin import show_admin_page


def configure_streamlit():
    """Configura la aplicación Streamlit"""
    st.set_page_config(**Config.get_streamlit_config())


def show_header():
    """Muestra el header principal de la aplicación"""
    # Verificar si el usuario está autenticado
    if StreamlitAuth.is_authenticated():
        user = StreamlitAuth.get_current_user()
        
        # Header con información del usuario
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
            st.subheader(Config.APP_DESCRIPTION)
        
        with col2:
            st.markdown(f"### Bienvenido, **{user['username']}** 👤")
            if user['is_admin']:
                st.markdown("🔑 **Administrador**")
        
        with col3:
            # Botones de navegación rápida
            if st.button("👤 Perfil", use_container_width=True):
                st.session_state.page_selection = "Perfil"
                st.rerun()
            
            if user['is_admin']:
                if st.button("👑 Admin", use_container_width=True):
                    st.session_state.page_selection = "Administración"
                    st.rerun()
            
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                StreamlitAuth.logout()
                st.success("✅ Sesión cerrada exitosamente")
                st.rerun()
    else:
        # Header para usuarios no autenticados
        st.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        st.subheader("🔐 Acceso Requerido")
        st.info("Por favor inicia sesión para acceder al sistema")


def show_sidebar():
    """Configura y muestra la barra lateral con navegación"""
    
    # Verificar autenticación
    if not StreamlitAuth.is_authenticated():
        # Sidebar para usuarios no autenticados
        st.sidebar.title("🔐 Acceso")
        st.sidebar.markdown("Inicia sesión para acceder al sistema completo")
        
        auth_option = st.sidebar.radio(
            "Opciones de Acceso",
            ["🔑 Iniciar Sesión", "📝 Registrarse"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ Información")
        st.sidebar.info("""
        **BolsaV1 v3.0** ahora incluye:
        - 🔐 Sistema de autenticación
        - 👥 Soporte multi-usuario
        - 📊 Datos personalizados por usuario
        - 🔒 Seguridad mejorada
        """)
        
        return auth_option
    
    # Sidebar para usuarios autenticados
    user = StreamlitAuth.get_current_user()
    
    st.sidebar.title("🧭 Navegación")
    st.sidebar.markdown(f"Conectado como: **{user['username']}**")
    
    # Menú principal
    main_pages = [
        "📊 Valores",
        "📈 Cotizaciones", 
        "💼 Operaciones",
        "📋 Posiciones",
        "📜 Histórico"
    ]
    
    # Páginas de usuario
    user_pages = ["👤 Perfil"]
    
    # Páginas de administrador (solo para admins)
    admin_pages = []
    if user['is_admin']:
        admin_pages = ["👑 Administración"]
    
    # Combinar todas las páginas
    all_pages = main_pages + user_pages + admin_pages
    
    # Selector de página
    menu = st.sidebar.selectbox(
        "Seleccionar Página",
        all_pages,
        index=0,
        key="main_navigation"
    )
    
    # Información del usuario en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Tu Cuenta")
    
    # Estadísticas rápidas del usuario
    try:
        from app.services.user_service import UserService
        user_stats = UserService.get_user_statistics(user['id'])
        
        st.sidebar.metric("📊 Activos", user_stats.get('total_activos', 0))
        st.sidebar.metric("💼 Operaciones", user_stats.get('total_operaciones', 0))
        st.sidebar.metric("📈 Posiciones", user_stats.get('total_posiciones', 0))
        
    except Exception as e:
        logger = get_logger('sidebar')
        logger.warning(f"Error obteniendo estadísticas: {e}")
        st.sidebar.info("📊 Estadísticas no disponibles")
    
    # Información adicional
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Sistema")
    st.sidebar.info(f"""
    **Versión:** {Config.APP_VERSION}
    
    **Características FASE 3:**
    - � Autenticación segura
    - � Multi-usuario
    - � Datos personalizados
    - � Sesiones seguras
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
        # Páginas de autenticación (sin autenticación requerida)
        if menu_selection == "🔑 Iniciar Sesión":
            show_login_page()
            return
        elif menu_selection == "📝 Registrarse":
            show_register_page()
            return
        
        # Verificar autenticación para páginas protegidas
        if not StreamlitAuth.is_authenticated():
            st.warning("🔐 Debes iniciar sesión para acceder a esta página")
            show_login_page()
            return
        
        # Ruteo de páginas principales (requieren autenticación)
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
        
        # Mostrar información de debugging en modo desarrollo
        if Config.LOG_LEVEL == "DEBUG":
            with st.expander("🔍 Información de Debug"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())


def show_footer():
    """Muestra el footer de la aplicación"""
    st.markdown("---")
    
    # Verificar si el usuario está autenticado para mostrar información personalizada
    if StreamlitAuth.is_authenticated():
        user = StreamlitAuth.get_current_user()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("🔄 **Estado del Sistema**: ✅ Funcionando")
        
        with col2:
            st.markdown(f"🗂️ **Base de Datos**: PostgreSQL")
        
        with col3:
            st.markdown(f"📊 **API**: Yahoo Finance")
        
        with col4:
            st.markdown(f"👤 **Usuario**: {user['username']}")
        
        # Información adicional para administradores
        if user['is_admin']:
            st.markdown("---")
            try:
                from app.services.user_service import UserService
                admin_stats = UserService.get_admin_statistics()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("👥 Total Usuarios", admin_stats['total_users'])
                
                with col2:
                    st.metric("✅ Usuarios Activos", admin_stats['active_users'])
                
                with col3:
                    st.metric("📱 Sesiones Activas", admin_stats['active_sessions'])
                
                with col4:
                    st.metric("👑 Administradores", admin_stats['admin_users'])
            except:
                pass  # Fallo silencioso si no se pueden obtener estadísticas
    else:
        # Footer simple para usuarios no autenticados
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
        f"© 2024 {Config.APP_NAME} v{Config.APP_VERSION} - Sistema de Gestión de Activos Financieros con Autenticación"
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
    
    # Inicializar sistema de autenticación
    StreamlitAuth.initialize()
    
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