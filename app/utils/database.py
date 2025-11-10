"""
Configuración de Base de Datos

Este módulo contiene utilidades para la configuración e inicialización
de la base de datos PostgreSQL.
"""

import logging
from sqlalchemy import text
from ..models import Base, engine, SessionLocal

# Configurar logger
logger = logging.getLogger(__name__)


def init_database():
    """
    Crea todas las tablas en la base de datos
    
    Returns:
        bool: True si la inicialización fue exitosa, False en caso contrario
    """
    try:
        logger.info("Inicializando base de dados...")
        
        # Testar conexão primeiro
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        
        # Criar tabelas se não existirem
        Base.metadata.create_all(bind=engine)
        
        logger.info("Base de dados inicializada com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao inicializar base de dados: {e}")
        return False


def test_connection():
    """
    Testa la conexión a la base de datos
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except Exception as e:
        logger.error(f"Erro de conexão com a base de dados: {e}")
        return False