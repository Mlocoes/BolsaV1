"""
Servicio de Autenticación para BolsaV1

Este servicio maneja el login, logout, registro y gestión de sesiones
de usuarios con seguridad robusta.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import streamlit as st

from app.models import User, UserSession, SessionLocal
from app.utils.security import (
    hash_password, verify_password, generate_session_id, 
    create_jwt_token, decode_jwt_token, hash_session_data,
    is_password_strong, sanitize_username, validate_email
)
from app.utils.config import Config
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class AuthService:
    """Servicio de autenticación centralizado"""
    
    @staticmethod
    def register_user(
        username: str, 
        email: str, 
        password: str, 
        full_name: Optional[str] = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Registra un nuevo usuario
        
        Args:
            username: Nombre de usuario único
            email: Email único del usuario
            password: Contraseña en texto plano
            full_name: Nombre completo opcional
            
        Returns:
            Tupla (éxito, mensaje, usuario_creado)
        """
        session = SessionLocal()
        
        try:
            # Validar datos de entrada
            username = sanitize_username(username)
            
            if not validate_email(email):
                return False, "Email inválido", None
            
            is_strong, password_errors = is_password_strong(password)
            if not is_strong:
                return False, "; ".join(password_errors), None
            
            # Verificar que el usuario no exista
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    return False, "El nombre de usuario ya existe", None
                else:
                    return False, "El email ya está registrado", None
            
            # Crear nuevo usuario
            hashed_pwd = hash_password(password)
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_pwd,
                full_name=full_name,
                is_active=True,
                is_admin=False
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            logger.info(f"Nuevo usuario registrado: {username} ({email})")
            return True, "Usuario registrado exitosamente", new_user
            
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Error de integridad al registrar usuario: {e}")
            return False, "Error al crear usuario - datos duplicados", None
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error al registrar usuario: {e}", exc_info=True)
            return False, "Error interno del servidor", None
            
        finally:
            session.close()
    
    @staticmethod
    def login_user(
        username: str, 
        password: str, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Autentica un usuario y crea sesión
        
        Args:
            username: Nombre de usuario o email
            password: Contraseña en texto plano
            ip_address: IP del cliente
            user_agent: User agent del navegador
            
        Returns:
            Tupla (éxito, mensaje, datos_sesion)
        """
        session = SessionLocal()
        
        try:
            # Buscar usuario por username o email
            user = session.query(User).filter(
                (User.username == username.lower()) | 
                (User.email == username.lower())
            ).first()
            
            if not user:
                logger.warning(f"Intento de login con usuario inexistente: {username}")
                return False, "Credenciales inválidas", None
            
            if not user.is_active:
                logger.warning(f"Intento de login con usuario inactivo: {username}")
                return False, "Cuenta desactivada", None
            
            # Verificar contraseña
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Contraseña incorrecta para usuario: {username}")
                return False, "Credenciales inválidas", None
            
            # Crear sesión
            session_id = generate_session_id()
            expires_at = datetime.now(timezone.utc) + timedelta(hours=Config.SESSION_EXPIRE_HOURS)
            
            user_session = UserSession(
                user_id=user.id,
                session_id=session_id,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            session.add(user_session)
            
            # Actualizar último login
            user.last_login = datetime.now(timezone.utc)
            
            session.commit()
            session.refresh(user_session)
            
            # Crear token JWT
            token = create_jwt_token({
                "sub": user.username,
                "user_id": user.id,
                "session_id": session_id
            })
            
            logger.info(f"Login exitoso para usuario: {username}")
            
            return True, "Login exitoso", {
                "user": user.to_dict(),
                "session_id": session_id,
                "token": token,
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error en login: {e}", exc_info=True)
            return False, "Error interno del servidor", None
            
        finally:
            session.close()
    
    @staticmethod
    def logout_user(session_id: str) -> Tuple[bool, str]:
        """
        Cierra sesión de un usuario
        
        Args:
            session_id: ID de la sesión a cerrar
            
        Returns:
            Tupla (éxito, mensaje)
        """
        session = SessionLocal()
        
        try:
            user_session = session.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if user_session:
                user_session.revoke("user_logout")
                session.commit()
                logger.info(f"Session cerrada: {session_id}")
                return True, "Sesión cerrada exitosamente"
            else:
                return False, "Sesión no encontrada"
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error al cerrar sesión: {e}", exc_info=True)
            return False, "Error al cerrar sesión"
            
        finally:
            session.close()
    
    @staticmethod
    def validate_session(session_id: str) -> Tuple[bool, Optional[User]]:
        """
        Valida una sesión activa
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Tupla (es_válida, usuario)
        """
        session = SessionLocal()
        
        try:
            user_session = session.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if not user_session:
                return False, None
            
            if not user_session.is_valid:
                logger.warning(f"Sesión inválida o expirada: {session_id}")
                return False, None
            
            # Actualizar última actividad
            user_session.update_activity()
            session.commit()
            
            # Obtener usuario
            user = session.query(User).filter(User.id == user_session.user_id).first()
            
            if not user or not user.is_active:
                return False, None
            
            return True, user
            
        except Exception as e:
            logger.error(f"Error validando sesión: {e}", exc_info=True)
            return False, None
            
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
            user = session.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            return user
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return None
            
        finally:
            session.close()
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Cambia la contraseña de un usuario
        
        Args:
            user_id: ID del usuario
            old_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            Tupla (éxito, mensaje)
        """
        session = SessionLocal()
        
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Usuario no encontrado"
            
            # Verificar contraseña actual
            if not verify_password(old_password, user.hashed_password):
                return False, "Contraseña actual incorrecta"
            
            # Validar nueva contraseña
            is_strong, password_errors = is_password_strong(new_password)
            if not is_strong:
                return False, "; ".join(password_errors)
            
            # Actualizar contraseña
            user.hashed_password = hash_password(new_password)
            user.updated_at = datetime.now(timezone.utc)
            
            session.commit()
            
            logger.info(f"Contraseña cambiada para usuario: {user.username}")
            return True, "Contraseña actualizada exitosamente"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error cambiando contraseña: {e}", exc_info=True)
            return False, "Error interno del servidor"
            
        finally:
            session.close()
    
    @staticmethod
    def revoke_all_user_sessions(user_id: int) -> Tuple[bool, str]:
        """
        Revoca todas las sesiones de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Tupla (éxito, mensaje)
        """
        session = SessionLocal()
        
        try:
            sessions = session.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False
            ).all()
            
            for user_session in sessions:
                user_session.revoke("admin_revoke")
            
            session.commit()
            
            logger.info(f"Todas las sesiones revocadas para usuario ID: {user_id}")
            return True, f"Se revocaron {len(sessions)} sesiones"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error revocando sesiones: {e}", exc_info=True)
            return False, "Error al revocar sesiones"
            
        finally:
            session.close()
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Limpia sesiones expiradas del sistema
        
        Returns:
            Número de sesiones eliminadas
        """
        session = SessionLocal()
        
        try:
            expired_count = session.query(UserSession).filter(
                UserSession.expires_at < datetime.now(timezone.utc)
            ).count()
            
            session.query(UserSession).filter(
                UserSession.expires_at < datetime.now(timezone.utc)
            ).delete()
            
            session.commit()
            
            if expired_count > 0:
                logger.info(f"Limpiadas {expired_count} sesiones expiradas")
            
            return expired_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error limpiando sesiones expiradas: {e}", exc_info=True)
            return 0
            
        finally:
            session.close()