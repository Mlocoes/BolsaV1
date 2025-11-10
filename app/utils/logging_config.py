"""
Utilidades de Logging

Este módulo configura el sistema de logging para BolsaV1.
"""

import os
import logging
import logging.handlers
from .config import Config


def setup_logging() -> logging.Logger:
    """
    Configura el sistema de logging de la aplicación
    
    Returns:
        logging.Logger: Logger principal configurado
    """
    # Crear directorio de logs si no existe
    try:
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        os.chmod(Config.LOG_DIR, 0o755)
    except Exception as e:
        print(f"Warning: No se pudo crear directorio logs: {e}")
    
    # Configurar logging principal
    logger = logging.getLogger('bolsav1')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Evitar duplicación si ya está configurado
    if logger.handlers:
        return logger
    
    # Crear formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo con rotación
    try:
        log_file_path = os.path.join(Config.LOG_DIR, Config.LOG_FILE)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: No se pudo configurar logging a archivo: {e}")
    
    # Handler para consola (fallback)
    try:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Solo warnings y errores en consola
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    except Exception as e:
        print(f"Warning: No se pudo configurar logging a consola: {e}")
    
    # Configurar loggers de terceros
    logging.getLogger('yfinance').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logger.info(f"Sistema de logging inicializado - Nivel: {Config.LOG_LEVEL}")
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtiene un logger específico para un módulo
    
    Args:
        name: Nombre del módulo/logger
        
    Returns:
        logging.Logger: Logger específico
    """
    if name:
        return logging.getLogger(f'bolsav1.{name}')
    else:
        return logging.getLogger('bolsav1')