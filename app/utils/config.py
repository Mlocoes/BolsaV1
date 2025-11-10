"""
Configuración de la Aplicación

Este módulo contiene todas las configuraciones centralizadas de BolsaV1.
"""

import os
from typing import Dict, Any


class Config:
    """Configuración principal de la aplicación"""
    
    # Base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bolsa_user:bolsa_password_2025@localhost:5432/stock_management"
    )
    
    # Cache de cotizaciones
    CACHE_TIMEOUT: int = int(os.getenv("CACHE_TIMEOUT", "300"))  # 5 minutos
    
    # Yahoo Finance
    REQUEST_DELAY_MIN: float = float(os.getenv("REQUEST_DELAY_MIN", "1.0"))
    REQUEST_DELAY_MAX: float = float(os.getenv("REQUEST_DELAY_MAX", "3.0"))
    YAHOO_TIMEOUT: int = int(os.getenv("YAHOO_TIMEOUT", "15"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_FILE: str = os.getenv("LOG_FILE", "bolsav1.log")
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Streamlit
    PAGE_TITLE: str = "BolsaV1 - Stock Management System"
    PAGE_ICON: str = "📈"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"
    
    # Aplicación
    APP_VERSION: str = "3.0.0"
    APP_NAME: str = "BolsaV1"
    APP_DESCRIPTION: str = "Sistema Integral de Gestión de Activos Financieros"
    
    # Seguridad y Autenticación (FASE 3)
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "default-dev-key-change-in-production-bolsav1-2024-security"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas
    JWT_ALGORITHM: str = "HS256"
    SESSION_EXPIRE_HOURS: int = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = int(os.getenv("LOGIN_ATTEMPT_WINDOW_MINUTES", "15"))
    
    @classmethod
    def get_streamlit_config(cls) -> Dict[str, Any]:
        """Retorna configuración para Streamlit"""
        return {
            "page_title": cls.PAGE_TITLE,
            "page_icon": cls.PAGE_ICON,
            "layout": cls.LAYOUT,
            "initial_sidebar_state": cls.INITIAL_SIDEBAR_STATE
        }
    
    @classmethod
    def get_db_config(cls) -> Dict[str, Any]:
        """Retorna configuración de base de datos"""
        return {
            "database_url": cls.DATABASE_URL
        }
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Retorna configuración de cache"""
        return {
            "timeout": cls.CACHE_TIMEOUT
        }
    
    @classmethod
    def get_yahoo_config(cls) -> Dict[str, Any]:
        """Retorna configuración para Yahoo Finance"""
        return {
            "request_delay_min": cls.REQUEST_DELAY_MIN,
            "request_delay_max": cls.REQUEST_DELAY_MAX,
            "timeout": cls.YAHOO_TIMEOUT
        }
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Retorna configuración de seguridad"""
        return {
            "secret_key": cls.SECRET_KEY,
            "access_token_expire_minutes": cls.ACCESS_TOKEN_EXPIRE_MINUTES,
            "jwt_algorithm": cls.JWT_ALGORITHM,
            "session_expire_hours": cls.SESSION_EXPIRE_HOURS,
            "password_min_length": cls.PASSWORD_MIN_LENGTH,
            "max_login_attempts": cls.MAX_LOGIN_ATTEMPTS,
            "login_attempt_window_minutes": cls.LOGIN_ATTEMPT_WINDOW_MINUTES
        }
    
    @classmethod
    def get_secret_key(cls) -> str:
        """Retorna la clave secreta para JWT"""
        return cls.SECRET_KEY
    
    @classmethod
    def is_production(cls) -> bool:
        """Determina si estamos en entorno de producción"""
        return cls.LOG_LEVEL == "INFO"
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Retorna configuración de logging"""
        return {
            "level": cls.LOG_LEVEL,
            "log_dir": cls.LOG_DIR,
            "log_file": cls.LOG_FILE,
            "max_bytes": cls.LOG_MAX_BYTES,
            "backup_count": cls.LOG_BACKUP_COUNT
        }


# Tickers conocidos para validación offline
KNOWN_TICKERS = {
    'NVDA': 'NVIDIA Corporation',
    'NVIDIA': 'NVDA',  # Redirect común
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc. (Class A)',
    'GOOG': 'Alphabet Inc. (Class C)',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'META': 'Meta Platforms Inc.',
    'NFLX': 'Netflix Inc.',
    'AMD': 'Advanced Micro Devices Inc.',
    'INTC': 'Intel Corporation',
    'CRM': 'Salesforce Inc.',
    'PYPL': 'PayPal Holdings Inc.',
    'ADBE': 'Adobe Inc.',
    'NDAQ': 'Nasdaq Inc.',
    'UBER': 'Uber Technologies Inc.',
    'SQ': 'Block Inc.',
    'ZOOM': 'Zoom Video Communications Inc.',
    'SHOP': 'Shopify Inc.',
    'SPOT': 'Spotify Technology S.A.',
    'ROKU': 'Roku Inc.',
    'TWTR': 'Twitter Inc.',  # Histórico
    'SNAP': 'Snap Inc.',
    'PIN': 'Pinterest Inc.',
    'ABNB': 'Airbnb Inc.',
    'COIN': 'Coinbase Global Inc.',
    'RBLX': 'Roblox Corporation'
}

# Configuraciones por defecto para desarrollo
DEV_CONFIG = {
    "database_url": "postgresql://postgres:postgres@localhost:5432/stock_management",
    "cache_timeout": 300,
    "log_level": "DEBUG",
    "yahoo_timeout": 10
}

# Configuraciones para producción
PROD_CONFIG = {
    "cache_timeout": 600,  # 10 minutos en producción
    "log_level": "INFO",
    "yahoo_timeout": 20
}