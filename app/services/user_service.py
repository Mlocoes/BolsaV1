"""
Servicio de Gestión de Usuarios para BolsaV1

Este servicio maneja operaciones CRUD de usuarios y administración
de perfiles de usuario.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models import User, UserSession, SessionLocal
from app.utils.security import hash_password, sanitize_username, validate_email
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class UserService:
    """Servicio de gestión de usuarios"""
    
    @staticmethod
    def get_all_users(include_inactive: bool = False) -> List[User]:
        """
        Obtiene lista de todos los usuarios
        
        Args:
            include_inactive: Si incluir usuarios inactivos
            
        Returns:
            Lista de usuarios
        """
        session = SessionLocal()
        
        try:
            query = session.query(User)
            
            if not include_inactive:
                query = query.filter(User.is_active == True)
            
            users = query.order_by(User.created_at.desc()).all()
            return users
            
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}", exc_info=True)
            return []
            
        finally:
            session.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Obtiene un usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario o None si no existe
        """
        session = SessionLocal()
        
        try:
            user = session.query(User).filter(User.id == user_id).first()
            return user
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return None
            
        finally:
            session.close()
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Obtiene un usuario por nombre de usuario
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Usuario o None si no existe
        """
        session = SessionLocal()
        
        try:
            user = session.query(User).filter(
                User.username == username.lower()
            ).first()
            return user
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario {username}: {e}")
            return None
            
        finally:
            session.close()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Obtiene un usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario o None si no existe
        """
        session = SessionLocal()
        
        try:
            user = session.query(User).filter(
                User.email == email.lower()
            ).first()
            return user
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email {email}: {e}")
            return None
            
        finally:
            session.close()
    
    @staticmethod
    def update_user_profile(
        user_id: int,
        full_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Actualiza el perfil de un usuario
        
        Args:
            user_id: ID del usuario
            full_name: Nombre completo nuevo
            bio: Biografía nueva
            avatar_url: URL del avatar nuevo
            
        Returns:
            Tupla (éxito, mensaje)
        """
        session = SessionLocal()
        
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Usuario no encontrado"
            
            # Actualizar campos si se proporcionan
            if full_name is not None:
                user.full_name = full_name.strip() if full_name else None
            
            if bio is not None:
                user.bio = bio.strip() if bio else None
            
            if avatar_url is not None:
                user.avatar_url = avatar_url.strip() if avatar_url else None
            
            user.updated_at = datetime.now(timezone.utc)
            session.commit()
            
            logger.info(f"Perfil actualizado para usuario: {user.username}")
            return True, "Perfil actualizado exitosamente"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error actualizando perfil usuario {user_id}: {e}", exc_info=True)
            return False, "Error al actualizar perfil"
            
        finally:
            session.close()
    
    @staticmethod
    def deactivate_user(user_id: int, admin_user_id: int) -> Tuple[bool, str]:
        """
        Desactiva un usuario (solo admin)
        
        Args:
            user_id: ID del usuario a desactivar
            admin_user_id: ID del administrador que realiza la acción
            
        Returns:
            Tupla (éxito, mensaje)
        """
        session = SessionLocal()
        
        try:
            # Verificar que el admin existe y es admin
            admin = session.query(User).filter(
                User.id == admin_user_id,
                User.is_admin == True,
                User.is_active == True
            ).first()
            
            if not admin:
                return False, "Permisos insuficientes"
            
            # Obtener usuario a desactivar
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Usuario no encontrado"
            
            if user.is_admin and user.id != admin_user_id:
                return False, "No se puede desactivar otro administrador"
            
            # Desactivar usuario
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            
            # Revocar todas las sesiones del usuario
            sessions = session.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False
            ).all()
            
            for user_session in sessions:
                user_session.revoke("admin_deactivate")
            
            session.commit()
            
            logger.info(f"Usuario {user.username} desactivado por admin {admin.username}")
            return True, f"Usuario {user.username} desactivado exitosamente"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error desactivando usuario {user_id}: {e}", exc_info=True)
            return False, "Error al desactivar usuario"
            
        finally:
            session.close()
    
    @staticmethod
    def activate_user(user_id: int, admin_user_id: int) -> Tuple[bool, str]:
        """
        Activa un usuario (solo admin)
        
        Args:
            user_id: ID del usuario a activar
            admin_user_id: ID del administrador que realiza la acción
            
        Returns:
            Tupla (éxito, mensaje)
        """
        session = SessionLocal()
        
        try:
            # Verificar que el admin existe y es admin
            admin = session.query(User).filter(
                User.id == admin_user_id,
                User.is_admin == True,
                User.is_active == True
            ).first()
            
            if not admin:
                return False, "Permisos insuficientes"
            
            # Obtener usuario a activar
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Usuario no encontrado"
            
            # Activar usuario
            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)
            
            session.commit()
            
            logger.info(f"Usuario {user.username} activado por admin {admin.username}")
            return True, f"Usuario {user.username} activado exitosamente"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error activando usuario {user_id}: {e}", exc_info=True)
            return False, "Error al activar usuario"
            
        finally:
            session.close()
    
    @staticmethod
    def promote_to_admin(user_id: int, admin_user_id: int) -> Tuple[bool, str]:
        """
        Promociona un usuario a administrador
        
        Args:
            user_id: ID del usuario a promocionar
            admin_user_id: ID del administrador que realiza la acción
            
        Returns:
            Tupla (éxito, mensaje)
        """
        session = SessionLocal()
        
        try:
            # Verificar que el admin existe y es admin
            admin = session.query(User).filter(
                User.id == admin_user_id,
                User.is_admin == True,
                User.is_active == True
            ).first()
            
            if not admin:
                return False, "Permisos insuficientes"
            
            # Obtener usuario a promocionar
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Usuario no encontrado"
            
            if user.is_admin:
                return False, "El usuario ya es administrador"
            
            # Promocionar usuario
            user.is_admin = True
            user.updated_at = datetime.now(timezone.utc)
            
            session.commit()
            
            logger.info(f"Usuario {user.username} promocionado a admin por {admin.username}")
            return True, f"Usuario {user.username} promocionado a administrador"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error promocionando usuario {user_id}: {e}", exc_info=True)
            return False, "Error al promocionar usuario"
            
        finally:
            session.close()
    
    @staticmethod
    def get_user_statistics() -> Dict[str, Any]:
        """
        Obtiene estadísticas de usuarios del sistema
        
        Returns:
            Diccionario con estadísticas
        """
        session = SessionLocal()
        
        try:
            total_users = session.query(User).count()
            active_users = session.query(User).filter(User.is_active == True).count()
            inactive_users = total_users - active_users
            admin_users = session.query(User).filter(
                User.is_admin == True,
                User.is_active == True
            ).count()
            
            # Usuarios registrados en los últimos 30 días
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_users = session.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()
            
            # Usuarios con login reciente (últimos 7 días)
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_logins = session.query(User).filter(
                User.last_login >= seven_days_ago
            ).count()
            
            # Sesiones activas
            active_sessions = session.query(UserSession).filter(
                UserSession.expires_at > datetime.now(timezone.utc),
                UserSession.is_revoked == False
            ).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "admin_users": admin_users,
                "recent_registrations": recent_users,
                "recent_logins": recent_logins,
                "active_sessions": active_sessions
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
            return {}
            
        finally:
            session.close()
    
    @staticmethod
    def get_user_sessions(user_id: int) -> List[UserSession]:
        """
        Obtiene las sesiones activas de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de sesiones del usuario
        """
        session = SessionLocal()
        
        try:
            sessions = session.query(UserSession).filter(
                UserSession.user_id == user_id
            ).order_by(desc(UserSession.created_at)).all()
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error obteniendo sesiones del usuario {user_id}: {e}")
            return []
            
        finally:
            session.close()
    
    @staticmethod
    def create_admin_user(
        username: str,
        email: str, 
        password: str,
        full_name: Optional[str] = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Crea un usuario administrador
        
        Args:
            username: Nombre de usuario
            email: Email del admin
            password: Contraseña
            full_name: Nombre completo opcional
            
        Returns:
            Tupla (éxito, mensaje, usuario_creado)
        """
        session = SessionLocal()
        
        try:
            # Verificar si ya existe
            existing_user = session.query(User).filter(
                (User.username == username.lower()) | 
                (User.email == email.lower())
            ).first()
            
            if existing_user:
                return False, "Usuario o email ya existe", None
            
            # Crear admin
            hashed_password = hash_password(password)
            admin_user = User(
                username=sanitize_username(username),
                email=email.lower(),
                hashed_password=hashed_password,
                full_name=full_name,
                is_active=True,
                is_admin=True
            )
            
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            
            logger.info(f"Administrador creado: {username}")
            return True, "Administrador creado exitosamente", admin_user
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creando admin: {e}", exc_info=True)
            return False, "Error creando administrador", None
            
        finally:
            session.close()