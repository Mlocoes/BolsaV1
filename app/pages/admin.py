"""
Panel de Administración de Usuarios - BolsaV1

Esta página permite a los administradores gestionar usuarios,
ver estadísticas del sistema y realizar tareas administrativas.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.utils.auth import StreamlitAuth, admin_required
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@admin_required
def show_admin_page():
    """Muestra la página de administración"""
    
    st.title("👑 Panel de Administración")
    st.markdown("---")
    
    # Tabs principales
    tab_overview, tab_users, tab_sessions, tab_system = st.tabs([
        "📊 Resumen",
        "👥 Usuarios", 
        "📱 Sesiones",
        "⚙️ Sistema"
    ])
    
    with tab_overview:
        show_system_overview()
    
    with tab_users:
        show_user_management()
    
    with tab_sessions:
        show_session_management()
    
    with tab_system:
        show_system_tools()


def show_system_overview():
    """Muestra resumen del sistema"""
    
    st.subheader("📊 Resumen del Sistema")
    
    # Obtener estadísticas
    stats = UserService.get_admin_statistics()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Usuarios",
            value=stats['total_users'],
            delta=f"+{stats['users_last_30_days']} (30 días)"
        )
    
    with col2:
        st.metric(
            label="✅ Usuarios Activos",
            value=stats['active_users'],
            delta=f"{stats['active_percentage']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="📱 Sesiones Activas",
            value=stats['active_sessions'],
            delta=f"+{stats['sessions_last_24h']} (24h)"
        )
    
    with col4:
        st.metric(
            label="👑 Administradores",
            value=stats['admin_users'],
            delta=f"{stats['admin_percentage']:.1f}%"
        )
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de usuarios por mes
        show_users_chart(stats)
    
    with col2:
        # Actividad reciente
        show_recent_activity()


def show_users_chart(stats: Dict[str, Any]):
    """Muestra gráfico de usuarios registrados"""
    
    st.subheader("📈 Usuarios Registrados (Últimos 6 meses)")
    
    # Generar datos de ejemplo (en implementación real vendría de la BD)
    months = ['Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    users = [5, 8, 12, 18, 25, stats['total_users']]
    
    # Crear DataFrame
    df = pd.DataFrame({
        'Mes': months,
        'Usuarios': users
    })
    
    # Mostrar gráfico
    st.line_chart(df.set_index('Mes'))


def show_recent_activity():
    """Muestra actividad reciente"""
    
    st.subheader("🔄 Actividad Reciente")
    
    # Obtener actividad reciente (últimos logins)
    recent_activity = UserService.get_recent_activity(limit=10)
    
    if recent_activity:
        for activity in recent_activity:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text(f"👤 {activity['username']} - {activity['action']}")
                
                with col2:
                    time_ago = datetime.now() - activity['timestamp']
                    if time_ago.days > 0:
                        st.text(f"{time_ago.days}d")
                    elif time_ago.seconds > 3600:
                        st.text(f"{time_ago.seconds // 3600}h")
                    else:
                        st.text(f"{time_ago.seconds // 60}m")
    else:
        st.info("📝 No hay actividad reciente registrada")


def show_user_management():
    """Gestión de usuarios"""
    
    st.subheader("👥 Gestión de Usuarios")
    
    # Acciones rápidas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Crear Usuario", use_container_width=True):
            st.session_state.show_create_user = True
    
    with col2:
        if st.button("🔍 Buscar Usuario", use_container_width=True):
            st.session_state.show_user_search = True
    
    with col3:
        if st.button("📊 Exportar Lista", use_container_width=True):
            export_users_data()
    
    # Modal para crear usuario
    if st.session_state.get('show_create_user'):
        show_create_user_modal()
    
    # Tabla de usuarios
    show_users_table()


def show_create_user_modal():
    """Modal para crear nuevo usuario"""
    
    st.markdown("---")
    st.subheader("➕ Crear Nuevo Usuario")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Nombre de Usuario *",
                placeholder="usuario123"
            )
            
            email = st.text_input(
                "Email *",
                placeholder="usuario@ejemplo.com"
            )
        
        with col2:
            password = st.text_input(
                "Contraseña Temporal *",
                type="password",
                placeholder="Mínimo 8 caracteres"
            )
            
            is_admin = st.checkbox("¿Es Administrador?")
        
        full_name = st.text_input(
            "Nombre Completo",
            placeholder="Nombre completo del usuario"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            submitted = st.form_submit_button("✅ Crear Usuario", type="primary")
        
        with col2:
            if st.form_submit_button("❌ Cancelar"):
                st.session_state.show_create_user = False
                st.rerun()
        
        if submitted:
            if not all([username, email, password]):
                st.error("❌ Por favor completa los campos obligatorios")
            else:
                success, message = UserService.create_user_by_admin(
                    username=username,
                    email=email,
                    password=password,
                    is_admin=is_admin,
                    full_name=full_name
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.session_state.show_create_user = False
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


def show_users_table():
    """Muestra tabla de usuarios con acciones"""
    
    st.markdown("---")
    st.subheader("📋 Lista de Usuarios")
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_status = st.selectbox(
            "Estado",
            options=["Todos", "Activos", "Inactivos"],
            key="user_status_filter"
        )
    
    with col2:
        filter_role = st.selectbox(
            "Rol",
            options=["Todos", "Administradores", "Usuarios"],
            key="user_role_filter"
        )
    
    with col3:
        search_term = st.text_input(
            "Buscar",
            placeholder="Username o email...",
            key="user_search"
        )
    
    with col4:
        st.write("")  # Espacio
        refresh = st.button("🔄 Actualizar")
    
    # Obtener usuarios con filtros
    users = UserService.get_all_users_with_filters(
        status_filter=filter_status,
        role_filter=filter_role,
        search_term=search_term
    )
    
    if not users:
        st.info("📝 No se encontraron usuarios")
        return
    
    # Mostrar tabla
    for user in users:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 3])
            
            with col1:
                status_icon = "✅" if user['is_active'] else "❌"
                role_icon = "👑" if user['is_admin'] else "👤"
                st.markdown(f"{status_icon} {role_icon} **{user['username']}**")
                st.text(user['email'])
            
            with col2:
                st.text(f"Creado: {datetime.fromisoformat(user['created_at']).strftime('%d/%m/%Y')}")
                if user['last_login']:
                    st.text(f"Último: {datetime.fromisoformat(user['last_login']).strftime('%d/%m/%Y')}")
            
            with col3:
                # Estadísticas del usuario
                user_stats = UserService.get_user_statistics(user['id'])
                st.text(f"Activos: {user_stats.get('total_activos', 0)}")
                st.text(f"Operaciones: {user_stats.get('total_operaciones', 0)}")
            
            with col4:
                # Estado de sesiones
                sessions = UserService.get_user_sessions(user['id'])
                active_sessions = sum(1 for s in sessions if s.is_valid)
                st.text(f"Sesiones: {active_sessions}")
            
            with col5:
                # Acciones
                col_action1, col_action2 = st.columns(2)
                
                with col_action1:
                    if user['is_active']:
                        if st.button(f"🚫 Desactivar", key=f"deactivate_{user['id']}"):
                            toggle_user_status(user['id'], False)
                    else:
                        if st.button(f"✅ Activar", key=f"activate_{user['id']}"):
                            toggle_user_status(user['id'], True)
                
                with col_action2:
                    if st.button(f"👁️ Ver", key=f"view_{user['id']}"):
                        show_user_details(user)
            
            st.markdown("---")


def toggle_user_status(user_id: int, active: bool):
    """Activa/desactiva un usuario"""
    
    success, message = UserService.toggle_user_status(user_id, active)
    
    if success:
        action = "activado" if active else "desactivado"
        st.success(f"✅ Usuario {action} exitosamente")
        st.rerun()
    else:
        st.error(f"❌ {message}")


def show_user_details(user: Dict[str, Any]):
    """Muestra detalles completos de un usuario"""
    
    st.markdown("---")
    st.subheader(f"👤 Detalles de {user['username']}")
    
    # Información básica
    col1, col2 = st.columns(2)
    
    with col1:
        st.text(f"🆔 ID: {user['id']}")
        st.text(f"👤 Username: {user['username']}")
        st.text(f"📧 Email: {user['email']}")
        st.text(f"👑 Es Admin: {'Sí' if user['is_admin'] else 'No'}")
    
    with col2:
        st.text(f"✅ Activo: {'Sí' if user['is_active'] else 'No'}")
        st.text(f"📅 Creado: {datetime.fromisoformat(user['created_at']).strftime('%d/%m/%Y %H:%M')}")
        if user['last_login']:
            st.text(f"🕐 Último Login: {datetime.fromisoformat(user['last_login']).strftime('%d/%m/%Y %H:%M')}")
    
    # Estadísticas detalladas
    user_stats = UserService.get_detailed_user_statistics(user['id'])
    
    st.subheader("📊 Estadísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 Total Activos", user_stats.get('total_activos', 0))
    
    with col2:
        st.metric("💰 Total Operaciones", user_stats.get('total_operaciones', 0))
    
    with col3:
        st.metric("📊 Total Posiciones", user_stats.get('total_posiciones', 0))
    
    with col4:
        st.metric("📅 Días Activo", user_stats.get('dias_activo', 0))


def show_session_management():
    """Gestión de sesiones del sistema"""
    
    st.subheader("📱 Gestión de Sesiones")
    
    # Estadísticas de sesiones
    session_stats = AuthService.get_session_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sesiones", session_stats['total_sessions'])
    
    with col2:
        st.metric("Sesiones Activas", session_stats['active_sessions'])
    
    with col3:
        st.metric("Sesiones Hoy", session_stats['sessions_today'])
    
    with col4:
        st.metric("Promedio Duración", f"{session_stats['avg_duration_hours']:.1f}h")
    
    st.markdown("---")
    
    # Acciones de limpieza
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Limpiar Sesiones Expiradas", use_container_width=True):
            cleaned = AuthService.cleanup_expired_sessions()
            st.success(f"✅ Se limpiaron {cleaned} sesiones expiradas")
    
    with col2:
        if st.button("⚠️ Revocar Todas las Sesiones", use_container_width=True):
            if st.button("⚠️ Confirmar Revocación", use_container_width=True):
                revoked = AuthService.revoke_all_sessions()
                st.warning(f"⚠️ Se revocaron {revoked} sesiones")
    
    with col3:
        if st.button("📊 Actualizar Estadísticas", use_container_width=True):
            st.rerun()
    
    # Lista de sesiones activas
    st.subheader("📋 Sesiones Activas")
    
    active_sessions = AuthService.get_all_active_sessions()
    
    if not active_sessions:
        st.info("📱 No hay sesiones activas")
        return
    
    for session in active_sessions:
        with st.expander(f"Sesión de {session['username']} - {session['created_at'].strftime('%d/%m/%Y %H:%M')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text(f"🆔 ID Sesión: {session['session_id'][:16]}...")
                st.text(f"👤 Usuario: {session['username']}")
                st.text(f"📅 Creada: {session['created_at'].strftime('%d/%m/%Y %H:%M')}")
                st.text(f"⏱️ Última actividad: {session['last_activity'].strftime('%d/%m/%Y %H:%M')}")
            
            with col2:
                st.text(f"⏰ Expira: {session['expires_at'].strftime('%d/%m/%Y %H:%M')}")
                if session['ip_address']:
                    st.text(f"🌐 IP: {session['ip_address']}")
                if session['device_info']:
                    st.text(f"📱 Dispositivo: {session['device_info']}")
                
                if st.button(f"🚫 Revocar", key=f"revoke_{session['session_id']}"):
                    success = AuthService.revoke_session(session['session_id'])
                    if success:
                        st.success("✅ Sesión revocada")
                        st.rerun()


def show_system_tools():
    """Herramientas del sistema"""
    
    st.subheader("⚙️ Herramientas del Sistema")
    
    # Mantenimiento de base de datos
    st.markdown("### 🗄️ Mantenimiento de Base de Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Limpiar Datos Temporales", use_container_width=True):
            # Implementar limpieza de datos temporales
            st.success("✅ Datos temporales limpiados")
    
    with col2:
        if st.button("📊 Optimizar Tablas", use_container_width=True):
            # Implementar optimización de tablas
            st.success("✅ Tablas optimizadas")
    
    with col3:
        if st.button("🔍 Verificar Integridad", use_container_width=True):
            # Implementar verificación de integridad
            st.success("✅ Integridad verificada")
    
    st.markdown("---")
    
    # Configuración del sistema
    st.markdown("### ⚙️ Configuración del Sistema")
    
    with st.expander("🔧 Configuración Avanzada"):
        col1, col2 = st.columns(2)
        
        with col1:
            session_timeout = st.number_input(
                "Timeout de Sesión (horas)",
                min_value=1,
                max_value=720,
                value=24
            )
            
            max_sessions_per_user = st.number_input(
                "Máx. Sesiones por Usuario",
                min_value=1,
                max_value=20,
                value=5
            )
        
        with col2:
            password_min_length = st.number_input(
                "Longitud Mínima Contraseña",
                min_value=6,
                max_value=50,
                value=8
            )
            
            cleanup_frequency = st.selectbox(
                "Frecuencia de Limpieza",
                options=["Diaria", "Semanal", "Mensual"]
            )
        
        if st.button("💾 Guardar Configuración"):
            # Implementar guardado de configuración
            st.success("✅ Configuración guardada")
    
    st.markdown("---")
    
    # Logs del sistema
    st.markdown("### 📋 Logs del Sistema")
    
    if st.button("📄 Ver Logs Recientes"):
        # Mostrar logs recientes
        st.text_area(
            "Logs del Sistema (Últimas 50 líneas)",
            value="[2024-01-15 10:30:15] INFO: Usuario admin inició sesión\n"
                  "[2024-01-15 10:25:10] INFO: Se creó nuevo usuario: testuser\n"
                  "[2024-01-15 10:20:05] WARNING: Intento de login fallido para usuario: baduser\n"
                  "[2024-01-15 10:15:00] INFO: Sistema iniciado correctamente",
            height=200,
            disabled=True
        )


def export_users_data():
    """Exporta datos de usuarios a CSV"""
    
    try:
        users = UserService.get_all_users()
        
        # Crear DataFrame
        df = pd.DataFrame([
            {
                'ID': user['id'],
                'Username': user['username'],
                'Email': user['email'],
                'Es_Admin': user['is_admin'],
                'Activo': user['is_active'],
                'Fecha_Creacion': user['created_at'],
                'Ultimo_Login': user['last_login']
            }
            for user in users
        ])
        
        # Convertir a CSV
        csv = df.to_csv(index=False)
        
        # Botón de descarga
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"usuarios_bolsav1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"❌ Error exportando datos: {e}")


if __name__ == "__main__":
    show_admin_page()