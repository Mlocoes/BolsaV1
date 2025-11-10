"""
Utilidades de Seguridad para BolsaV1
"""
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from app.utils.config import Config

# Configuración de hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT
SECRET_KEY = Config.get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas


def hash_password(password: str) -> str:
    """
    Genera hash seguro de una contraseña
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña usando bcrypt
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado
        
    Returns:
        True si la contraseña es correcta
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_session_id() -> str:
    """
    Genera un ID de sesión único y seguro
    
    Returns:
        ID de sesión de 32 caracteres hexadecimales
    """
    return secrets.token_urlsafe(32)


def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica y valida un token JWT
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload del token o None si es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def generate_csrf_token() -> str:
    """
    Genera un token CSRF para protección contra ataques
    
    Returns:
        Token CSRF único
    """
    return secrets.token_urlsafe(32)


def hash_session_data(session_id: str, user_agent: str, ip_address: str) -> str:
    """
    Genera hash de datos de sesión para verificación de integridad
    
    Args:
        session_id: ID de la sesión
        user_agent: User agent del navegador
        ip_address: Dirección IP del usuario
        
    Returns:
        Hash SHA256 de los datos de sesión
    """
    data = f"{session_id}:{user_agent}:{ip_address}:{SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Valida si una contraseña cumple con los criterios de seguridad
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Tupla (es_válida, lista_errores)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")
    
    if not any(c.isupper() for c in password):
        errors.append("La contraseña debe tener al menos una mayúscula")
    
    if not any(c.islower() for c in password):
        errors.append("La contraseña debe tener al menos una minúscula")
    
    if not any(c.isdigit() for c in password):
        errors.append("La contraseña debe tener al menos un número")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("La contraseña debe tener al menos un carácter especial")
    
    return len(errors) == 0, errors


def sanitize_username(username: str) -> str:
    """
    Sanitiza un nombre de usuario
    
    Args:
        username: Nombre de usuario original
        
    Returns:
        Nombre de usuario sanitizado
    """
    # Convertir a minúsculas y remover espacios
    username = username.lower().strip()
    
    # Permitir solo caracteres alfanuméricos, guiones y underscores
    sanitized = ''.join(c for c in username if c.isalnum() or c in '-_')
    
    # Asegurar que no esté vacío
    if not sanitized:
        raise ValueError("El nombre de usuario no puede estar vacío")
    
    return sanitized


def validate_email(email: str) -> bool:
    """
    Valida un email básico
    
    Args:
        email: Email a validar
        
    Returns:
        True si el email parece válido
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_session_cookie_config() -> Dict[str, Any]:
    """
    Genera configuración segura para cookies de sesión
    
    Returns:
        Diccionario con configuración de cookies
    """
    is_production = Config.LOG_LEVEL == "INFO"
    
    return {
        "httponly": True,
        "secure": is_production,  # Solo HTTPS en producción
        "samesite": "lax",
        "max_age": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # En segundos
    }


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """
    Enmascara datos sensibles para logging
    
    Args:
        data: Dato sensible a enmascarar
        show_chars: Caracteres a mostrar al final
        
    Returns:
        Dato enmascarado
    """
    if not data or len(data) <= show_chars:
        return "*" * len(data) if data else ""
    
    return "*" * (len(data) - show_chars) + data[-show_chars:]