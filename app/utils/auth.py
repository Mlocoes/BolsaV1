"""
Utilidades de Autenticación para Streamlit

Este módulo contiene decoradores, middleware y utilidades para 
manejar autenticación y autorización en aplicaciones Streamlit.
"""

import functools
from typing import Optional, Dict, Any, Callable
import streamlit as st
from datetime import datetime, timezone

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models import User
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class StreamlitAuth:
    """Clase para manejar autenticación en Streamlit"""
    
    SESSION_KEY = "bolsav1_session_id"
    USER_KEY = "bolsav1_current_user"
    
    @staticmethod
    def initialize_session():
        """Inicializa las variables de sesión de autenticación"""
        if StreamlitAuth.SESSION_KEY not in st.session_state:
            st.session_state[StreamlitAuth.SESSION_KEY] = None
        
        if StreamlitAuth.USER_KEY not in st.session_state:
            st.session_state[StreamlitAuth.USER_KEY] = None
    
    @staticmethod
    def is_authenticated() -> bool:
        """
        Verifica si el usuario actual está autenticado
        
        Returns:
            True si está autenticado
        """
        StreamlitAuth.initialize_session()
        
        session_id = st.session_state.get(StreamlitAuth.SESSION_KEY)
        if not session_id:
            return False
        
        # Validar sesión con la base de datos
        is_valid, user = AuthService.validate_session(session_id)
        
        if is_valid and user:
            # Actualizar usuario en session state
            st.session_state[StreamlitAuth.USER_KEY] = user.to_dict()
            return True
        else:
            # Limpiar sesión inválida
            StreamlitAuth.logout()
            return False
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """
        Obtiene el usuario actual autenticado
        
        Returns:
            Diccionario con datos del usuario o None
        """
        if StreamlitAuth.is_authenticated():
            return st.session_state.get(StreamlitAuth.USER_KEY)
        return None
    
    @staticmethod
    def get_current_user_id() -> Optional[int]:
        """
        Obtiene el ID del usuario actual
        
        Returns:
            ID del usuario o None
        """
        user = StreamlitAuth.get_current_user()
        return user["id"] if user else None
    
    @staticmethod
    def is_admin() -> bool:
        """
        Verifica si el usuario actual es administrador
        
        Returns:
            True si es admin
        """
        user = StreamlitAuth.get_current_user()
        return user["is_admin"] if user else False
    
    @staticmethod
    def login(username: str, password: str) -> tuple[bool, str]:
        """
        Autentica un usuario
        
        Args:
            username: Nombre de usuario o email
            password: Contraseña
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Obtener información de la request (limitado en Streamlit)
        ip_address = None
        user_agent = None
        
        # Intentar login
        success, message, session_data = AuthService.login_user(
            username=username,
            password=password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if success and session_data:
            # Guardar datos de sesión en Streamlit
            st.session_state[StreamlitAuth.SESSION_KEY] = session_data["session_id"]
            st.session_state[StreamlitAuth.USER_KEY] = session_data["user"]
            
            logger.info(f"Login exitoso en Streamlit: {username}")
            return True, message
        else:
            return False, message
    
    @staticmethod
    def logout():
        """Cierra sesión del usuario actual"""
        session_id = st.session_state.get(StreamlitAuth.SESSION_KEY)
        
        if session_id:
            # Cerrar sesión en el servidor
            AuthService.logout_user(session_id)
        
        # Limpiar session state
        st.session_state[StreamlitAuth.SESSION_KEY] = None
        st.session_state[StreamlitAuth.USER_KEY] = None
        
        # Limpiar otros datos de sesión relacionados
        keys_to_clear = [key for key in st.session_state.keys() if key.startswith("bolsav1_")]
        for key in keys_to_clear:
            del st.session_state[key]
        
        logger.info("Logout exitoso en Streamlit")
    
    @staticmethod
    def require_auth(redirect_to_login: bool = True):
        """
        Decorator que requiere autenticación para una página
        
        Args:
            redirect_to_login: Si mostrar formulario de login
        """
        if not StreamlitAuth.is_authenticated():
            if redirect_to_login:
                StreamlitAuth.show_login_form()
            else:
                st.error("🔒 Acceso denegado. Debes iniciar sesión.")
                st.stop()
            return False
        return True
    
    @staticmethod
    def require_admin():
        """Decorator que requiere permisos de administrador"""
        if not StreamlitAuth.require_auth(redirect_to_login=True):
            return False
        
        if not StreamlitAuth.is_admin():
            st.error("🔒 Acceso denegado. Requiere permisos de administrador.")
            st.stop()
            return False
        
        return True
    
    @staticmethod
    def show_login_form():
        """Muestra formulario de login en la interfaz"""
        st.title("🔐 Iniciar Sesión - BolsaV1")
        
        # Centrar el formulario
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form"):
                st.markdown("### Acceso al Sistema")
                
                username = st.text_input(
                    "Usuario o Email",
                    placeholder="Ingresa tu nombre de usuario o email"
                )
                
                password = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="Ingresa tu contraseña"
                )
                
                col_login, col_register = st.columns(2)
                
                with col_login:
                    login_clicked = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
                
                with col_register:
                    if st.form_submit_button("📝 Registrarse", use_container_width=True):
                        st.session_state["show_register"] = True
                        st.rerun()
                
                if login_clicked:
                    if username and password:
                        success, message = StreamlitAuth.login(username, password)
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Por favor completa todos los campos")
        
        # Mostrar formulario de registro si se solicita
        if st.session_state.get("show_register", False):
            StreamlitAuth.show_register_form()
        
        # Información adicional
        with st.expander("ℹ️ Información del Sistema"):
            st.info("""
            **BolsaV1 v3.0.0** - Sistema de Gestión de Cartera con Autenticación
            
            🔐 **Características de Seguridad:**
            - Autenticación robusta con hashing bcrypt
            - Sesiones seguras con expiración automática
            - Aislamiento completo de datos por usuario
            - Panel administrativo para gestión de usuarios
            
            📧 **¿Primera vez?**
            Haz clic en "Registrarse" para crear tu cuenta gratuita.
            
            🔧 **¿Problemas técnicos?**
            Contacta al administrador del sistema.
            """)
    
    @staticmethod
    def show_register_form():
        """Muestra formulario de registro"""
        st.markdown("---")
        st.subheader("📝 Registro de Usuario")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input(
                    "Nombre de Usuario",
                    placeholder="ej: juan_investor"
                )
                email = st.text_input(
                    "Email",
                    placeholder="tu@email.com"
                )
            
            with col2:
                full_name = st.text_input(
                    "Nombre Completo",
                    placeholder="Juan Pérez"
                )
                password = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="Mínimo 8 caracteres"
                )
            
            col_back, col_submit = st.columns(2)
            
            with col_back:
                if st.form_submit_button("🔙 Volver al Login", use_container_width=True):
                    st.session_state["show_register"] = False
                    st.rerun()
            
            with col_submit:
                register_clicked = st.form_submit_button("✨ Crear Cuenta", use_container_width=True)
            
            if register_clicked:
                if username and email and password:
                    success, message, new_user = AuthService.register_user(
                        username=username,
                        email=email,
                        password=password,
                        full_name=full_name if full_name else None
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.info("🚀 Ahora puedes iniciar sesión con tu nueva cuenta")
                        st.session_state["show_register"] = False
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Por favor completa los campos requeridos (usuario, email, contraseña)")
    
    @staticmethod
    def show_user_info():
        """Muestra información del usuario en la sidebar"""
        user = StreamlitAuth.get_current_user()
        
        if user:
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 Usuario Actual")
                
                # Avatar (placeholder)
                st.markdown(f"**{user['display_name']}**")
                st.caption(f"@{user['username']}")
                
                if user['is_admin']:
                    st.badge("👑 Administrador", type="secondary")
                
                # Botones de acción
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("👤 Perfil", use_container_width=True):
                        st.session_state["show_profile"] = True
                
                with col2:
                    if st.button("🚪 Salir", use_container_width=True):
                        StreamlitAuth.logout()
                        st.rerun()


def login_required(func: Callable) -> Callable:
    """
    Decorator para funciones que requieren autenticación
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con verificación de autenticación
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not StreamlitAuth.require_auth():
            return None
        return func(*args, **kwargs)
    
    return wrapper


def admin_required(func: Callable) -> Callable:
    """
    Decorator para funciones que requieren permisos de admin
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con verificación de admin
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not StreamlitAuth.require_admin():
            return None
        return func(*args, **kwargs)
    
    return wrapper


def inject_user_context(func: Callable) -> Callable:
    """
    Decorator que inyecta el contexto del usuario en los argumentos
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con user_id inyectado
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = StreamlitAuth.get_current_user_id()
        if user_id:
            kwargs['user_id'] = user_id
        return func(*args, **kwargs)
    
    return wrapper