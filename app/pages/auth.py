"""
Páginas de Autenticación para BolsaV1

Este módulo contiene las pantallas de login, registro y gestión de acceso.
"""

import streamlit as st
from typing import Optional
from app.services.auth_service import AuthService
from app.utils.auth import StreamlitAuth
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def show_login_page():
    """Muestra la página de login"""
    st.markdown("---")
    
    # Header principal
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1>🔐 BolsaV1 Login</h1>
            <h3>Sistema de Gestión de Activos Financieros</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulario de login centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👤 Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input(
                "Usuario", 
                placeholder="Ingresa tu nombre de usuario",
                help="Usuario registrado en el sistema"
            )
            
            password = st.text_input(
                "Contraseña", 
                type="password",
                placeholder="Tu contraseña",
                help="Contraseña de tu cuenta"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            
            with col_b:
                submit_button = st.form_submit_button(
                    "🚀 Ingresar", 
                    use_container_width=True
                )
            
            if submit_button:
                if not username or not password:
                    st.error("❌ Por favor completa todos los campos")
                else:
                    # Intentar login
                    with st.spinner("🔄 Verificando credenciales..."):
                        success, message, session_data = AuthService.login_user(
                            username=username,
                            password=password,
                            ip_address=st.session_state.get("client_ip", "127.0.0.1"),
                            user_agent="Streamlit-Browser"
                        )
                    
                    if success:
                        # Login exitoso
                        StreamlitAuth.set_session_data(session_data)
                        st.success(f"✅ ¡Bienvenido {session_data['user']['full_name']}!")
                        st.balloons()
                        
                        # Rerun para actualizar la interfaz
                        st.rerun()
                    else:
                        # Login fallido
                        st.error(f"❌ {message}")
                        logger.warning(f"Login fallido para usuario: {username}")
    
    # Sección de registro
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 ¿No tienes cuenta?")
        
        if st.button("Crear nueva cuenta", use_container_width=True):
            st.session_state["show_register"] = True
            st.rerun()
    
    # Información del sistema
    st.markdown("---")
    
    with st.expander("ℹ️ Información del Sistema"):
        st.markdown("""
        **BolsaV1 v3.0.0** - Sistema Multi-Usuario
        
        **Características:**
        - 🔐 Autenticación segura
        - 👥 Multi-tenancy completo
        - 💹 Gestión personalizada de activos
        - 📊 Portfolios privados
        - 🔄 Cotizaciones en tiempo real
        
        **Usuarios de Prueba:**
        - **Admin**: admin / admin123
        
        **Soporte**: admin@bolsav1.com
        """)


def show_register_page():
    """Muestra la página de registro"""
    st.markdown("---")
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1>📝 Registro de Usuario</h1>
            <h3>Crear cuenta en BolsaV1</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulario de registro
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👤 Nueva Cuenta")
        
        with st.form("register_form"):
            username = st.text_input(
                "Nombre de Usuario",
                placeholder="Ej: juan_perez",
                help="Debe ser único en el sistema"
            )
            
            email = st.text_input(
                "Email",
                placeholder="usuario@email.com",
                help="Email válido para notificaciones"
            )
            
            full_name = st.text_input(
                "Nombre Completo",
                placeholder="Juan Pérez",
                help="Tu nombre completo"
            )
            
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Mínimo 8 caracteres",
                help="Debe incluir mayúsculas, números y caracteres especiales"
            )
            
            confirm_password = st.text_input(
                "Confirmar Contraseña",
                type="password",
                placeholder="Repite la contraseña"
            )
            
            # Términos y condiciones
            accept_terms = st.checkbox(
                "Acepto los términos y condiciones del sistema",
                help="Requerido para crear cuenta"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            
            with col_b:
                submit_button = st.form_submit_button(
                    "✨ Crear Cuenta",
                    use_container_width=True
                )
            
            if submit_button:
                # Validaciones
                errors = []
                
                if not all([username, email, full_name, password, confirm_password]):
                    errors.append("❌ Todos los campos son obligatorios")
                
                if password != confirm_password:
                    errors.append("❌ Las contraseñas no coinciden")
                
                if len(password) < 8:
                    errors.append("❌ La contraseña debe tener al menos 8 caracteres")
                
                if not accept_terms:
                    errors.append("❌ Debes aceptar los términos y condiciones")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Intentar registro
                    with st.spinner("🔄 Creando cuenta..."):
                        success, message, user = AuthService.register_user(
                            username=username,
                            email=email,
                            password=password,
                            full_name=full_name
                        )
                    
                    if success:
                        st.success(f"✅ ¡Cuenta creada exitosamente!")
                        st.info("🔄 Ahora puedes iniciar sesión con tus credenciales")
                        st.balloons()
                        
                        # Volver a login después de 3 segundos
                        if st.button("🔐 Ir a Login"):
                            st.session_state["show_register"] = False
                            st.rerun()
                    else:
                        st.error(f"❌ Error al crear cuenta: {message}")
    
    # Botón para volver al login
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("⬅️ Volver al Login", use_container_width=True):
            st.session_state["show_register"] = False
            st.rerun()


def show_logout_confirmation():
    """Muestra confirmación de logout"""
    st.warning("🔐 ¿Estás seguro que quieres cerrar sesión?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Sí, cerrar sesión", use_container_width=True):
            StreamlitAuth.logout()
            st.success("👋 Sesión cerrada exitosamente")
            st.rerun()
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state["show_logout"] = False
            st.rerun()