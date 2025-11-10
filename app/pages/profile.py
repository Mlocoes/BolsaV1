"""
Página de Perfil de Usuario - BolsaV1

Esta página permite a los usuarios gestionar su perfil personal,
cambiar contraseña y ver información de sus sesiones.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any

from app.utils.auth import StreamlitAuth, login_required
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@login_required
def show_profile_page():
    """Muestra la página de perfil de usuario"""
    
    st.title("👤 Mi Perfil")
    
    user = StreamlitAuth.get_current_user()
    if not user:
        st.error("Error obteniendo información del usuario")
        return
    
    # Tabs para organizar el contenido
    tab_profile, tab_security, tab_sessions = st.tabs([
        "📋 Información Personal", 
        "🔐 Seguridad", 
        "📱 Sesiones"
    ])
    
    with tab_profile:
        show_profile_info(user)
    
    with tab_security:
        show_security_settings(user)
    
    with tab_sessions:
        show_user_sessions(user)


def show_profile_info(user: Dict[str, Any]):
    """Muestra y permite editar información del perfil"""
    
    st.subheader("📝 Información Personal")
    
    # Información de solo lectura
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input(
            "Nombre de Usuario",
            value=user['username'],
            disabled=True,
            help="El nombre de usuario no se puede cambiar"
        )
        
        st.text_input(
            "Email",
            value=user['email'],
            disabled=True,
            help="El email no se puede cambiar"
        )
    
    with col2:
        st.text_input(
            "Miembro desde",
            value=datetime.fromisoformat(user['created_at']).strftime("%d/%m/%Y"),
            disabled=True
        )
        
        if user['last_login']:
            st.text_input(
                "Último acceso",
                value=datetime.fromisoformat(user['last_login']).strftime("%d/%m/%Y %H:%M"),
                disabled=True
            )
    
    st.markdown("---")
    
    # Información editable
    st.subheader("✏️ Información Editable")
    
    with st.form("profile_form"):
        full_name = st.text_input(
            "Nombre Completo",
            value=user.get('full_name', ''),
            placeholder="Tu nombre completo"
        )
        
        bio = st.text_area(
            "Biografía",
            value=user.get('bio', ''),
            placeholder="Cuéntanos algo sobre ti y tus objetivos de inversión...",
            max_chars=500
        )
        
        avatar_url = st.text_input(
            "URL de Avatar",
            value=user.get('avatar_url', ''),
            placeholder="https://ejemplo.com/tu-avatar.jpg"
        )
        
        submitted = st.form_submit_button("💾 Actualizar Perfil")
        
        if submitted:
            success, message = UserService.update_user_profile(
                user_id=user['id'],
                full_name=full_name,
                bio=bio,
                avatar_url=avatar_url
            )
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {message}")


def show_security_settings(user: Dict[str, Any]):
    """Muestra configuración de seguridad"""
    
    st.subheader("🔐 Configuración de Seguridad")
    
    # Estado de la cuenta
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if user['is_active']:
            st.success("✅ Cuenta Activa")
        else:
            st.error("❌ Cuenta Inactiva")
    
    with col2:
        if user['is_admin']:
            st.info("👑 Administrador")
        else:
            st.info("👤 Usuario Regular")
    
    with col3:
        # Obtener estadísticas de sesiones
        user_sessions = UserService.get_user_sessions(user['id'])
        active_sessions = sum(1 for s in user_sessions if s.is_valid)
        st.metric("Sesiones Activas", active_sessions)
    
    st.markdown("---")
    
    # Cambio de contraseña
    st.subheader("🔑 Cambiar Contraseña")
    
    with st.form("password_form"):
        current_password = st.text_input(
            "Contraseña Actual",
            type="password",
            placeholder="Ingresa tu contraseña actual"
        )
        
        new_password = st.text_input(
            "Nueva Contraseña",
            type="password",
            placeholder="Mínimo 8 caracteres"
        )
        
        confirm_password = st.text_input(
            "Confirmar Nueva Contraseña",
            type="password",
            placeholder="Confirma tu nueva contraseña"
        )
        
        change_password = st.form_submit_button("🔐 Cambiar Contraseña")
        
        if change_password:
            if not all([current_password, new_password, confirm_password]):
                st.error("❌ Por favor completa todos los campos")
            elif new_password != confirm_password:
                st.error("❌ Las nuevas contraseñas no coinciden")
            else:
                success, message = AuthService.change_password(
                    user_id=user['id'],
                    old_password=current_password,
                    new_password=new_password
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.info("🔄 Por favor inicia sesión nuevamente")
                    if st.button("🔄 Iniciar Sesión"):
                        StreamlitAuth.logout()
                        st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    st.markdown("---")
    
    # Acciones de seguridad
    st.subheader("⚠️ Acciones de Seguridad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚪 Cerrar Todas las Sesiones", use_container_width=True):
            success, message = AuthService.revoke_all_user_sessions(user['id'])
            if success:
                st.success(f"✅ {message}")
                st.info("🔄 Serás redirigido al login...")
                StreamlitAuth.logout()
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    with col2:
        if st.button("🔄 Refrescar Datos", use_container_width=True):
            st.rerun()


def show_user_sessions(user: Dict[str, Any]):
    """Muestra las sesiones del usuario"""
    
    st.subheader("📱 Mis Sesiones")
    
    # Obtener sesiones del usuario
    sessions = UserService.get_user_sessions(user['id'])
    
    if not sessions:
        st.info("📱 No tienes sesiones registradas")
        return
    
    # Separar sesiones activas y expiradas
    active_sessions = [s for s in sessions if s.is_valid]
    inactive_sessions = [s for s in sessions if not s.is_valid]
    
    # Mostrar estadísticas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sesiones", len(sessions))
    
    with col2:
        st.metric("Sesiones Activas", len(active_sessions))
    
    with col3:
        st.metric("Sesiones Inactivas", len(inactive_sessions))
    
    # Mostrar sesiones activas
    if active_sessions:
        st.markdown("### ✅ Sesiones Activas")
        
        for i, session in enumerate(active_sessions):
            with st.expander(f"Sesión {i+1} - {session.created_at.strftime('%d/%m/%Y %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text(f"🆔 ID: {session.session_id[:16]}...")
                    st.text(f"📅 Creada: {session.created_at.strftime('%d/%m/%Y %H:%M')}")
                    st.text(f"⏱️ Última actividad: {session.last_activity.strftime('%d/%m/%Y %H:%M')}")
                
                with col2:
                    st.text(f"⏰ Expira: {session.expires_at.strftime('%d/%m/%Y %H:%M')}")
                    if session.ip_address:
                        st.text(f"🌐 IP: {session.ip_address}")
                    if session.device_info:
                        st.text(f"📱 Dispositivo: {session.device_info}")
    
    # Mostrar sesiones inactivas (limitado)
    if inactive_sessions:
        st.markdown("### ❌ Sesiones Recientes Inactivas")
        
        # Mostrar solo las últimas 5 sesiones inactivas
        for session in inactive_sessions[:5]:
            with st.expander(f"Sesión - {session.created_at.strftime('%d/%m/%Y %H:%M')} (Inactiva)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text(f"📅 Creada: {session.created_at.strftime('%d/%m/%Y %H:%M')}")
                    if session.revoked_at:
                        st.text(f"🚫 Revocada: {session.revoked_at.strftime('%d/%m/%Y %H:%M')}")
                
                with col2:
                    if session.is_expired:
                        st.text("⏰ Estado: Expirada")
                    elif session.is_revoked:
                        st.text(f"🚫 Estado: Revocada ({session.revoked_reason})")
                    
                    if session.ip_address:
                        st.text(f"🌐 IP: {session.ip_address}")
    
    # Botón para limpiar sesiones expiradas
    if inactive_sessions:
        st.markdown("---")
        if st.button("🧹 Limpiar Sesiones Expiradas"):
            cleaned = AuthService.cleanup_expired_sessions()
            st.success(f"✅ Se limpiaron {cleaned} sesiones expiradas")
            st.rerun()


if __name__ == "__main__":
    show_profile_page()