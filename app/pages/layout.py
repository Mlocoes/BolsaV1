"""
Módulo de Layout - FASE 3

Este módulo contiene las funciones para renderizar el layout principal
de la aplicación, incluyendo header, sidebar y footer.
"""

import streamlit as st
from ..utils.auth import StreamlitAuth
from ..utils.config import Config


def show_header():
    """Muestra el header principal de la aplicación"""
    if StreamlitAuth.is_authenticated():
        user = StreamlitAuth.get_current_user()
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
            st.subheader(Config.APP_DESCRIPTION)
        with col2:
            st.markdown(f"### Bienvenido, **{user['username']}** 👤")
            if user['is_admin']:
                st.markdown("🔑 **Administrador**")
        with col3:
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
        st.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        st.subheader("🔐 Acceso Requerido")
        st.info("Por favor inicia sesión para acceder al sistema")


def show_sidebar():
    """Configura y muestra la barra lateral con navegación"""
    if not StreamlitAuth.is_authenticated():
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

    user = StreamlitAuth.get_current_user()
    st.sidebar.title("🧭 Navegación")
    st.sidebar.markdown(f"Conectado como: **{user['username']}**")
    main_pages = [
        "📊 Valores",
        "📈 Cotizaciones",
        "💼 Operaciones",
        "📋 Posiciones",
        "📜 Histórico"
    ]
    user_pages = ["👤 Perfil"]
    admin_pages = []
    if user['is_admin']:
        admin_pages = ["👑 Administración"]
    all_pages = main_pages + user_pages + admin_pages
    menu = st.sidebar.selectbox(
        "Seleccionar Página",
        all_pages,
        index=0,
        key="main_navigation"
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Tu Cuenta")
    try:
        from ..services.user_service import UserService
        user_stats = UserService.get_user_statistics()
        st.sidebar.metric("📊 Activos", user_stats.get('total_activos', 0))
        st.sidebar.metric("💼 Operaciones", user_stats.get('total_operaciones', 0))
        st.sidebar.metric("📈 Posiciones", user_stats.get('total_posiciones', 0))
    except Exception as e:
        from ..utils.logging_config import get_logger
        logger = get_logger('sidebar')
        logger.warning(f"Error obteniendo estadísticas: {e}")
        st.sidebar.info("📊 Estadísticas no disponibles")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Sistema")
    st.sidebar.info(f"""
    **Versión:** {Config.APP_VERSION}

    **Características FASE 3:**
    - 🔐 Autenticación segura
    - 👥 Multi-usuario
    - 📊 Datos personalizados
    - 🔒 Sesiones seguras
    """)
    return menu


def show_footer():
    """Muestra el footer de la aplicación"""
    st.markdown("---")
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
        if user['is_admin']:
            st.markdown("---")
            try:
                from ..services.user_service import UserService
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
                pass
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🔄 **Estado del Sistema**: ✅ Funcionando")
        with col2:
            st.markdown(f"🗂️ **Base de Datos**: PostgreSQL")
        with col3:
            st.markdown(f"📊 **API**: Yahoo Finance")
    st.markdown(
        "<div style='text-align: center; color: gray; padding: 10px;'>"
        f"© 2024 {Config.APP_NAME} v{Config.APP_VERSION} - Sistema de Gestión de Activos Financieros con Autenticación"
        "</div>",
        unsafe_allow_html=True
    )
