"""
Configuración base para modelos SQLAlchemy

Este módulo contiene la configuración base para todos los modelos
de la aplicación BolsaV1.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/stock_management"
)

# Base declarativa para todos los modelos
Base = declarative_base()

# Engine y sesión
engine = create_engine(DATABASE_URL)
_session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(_session_factory)

# Función para obtener sesión de base de datos
def get_db():
    """Generator que proporciona una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def remove_db_session():
    """Cierra y elimina la sesión de la base de datos del hilo actual."""
    SessionLocal.remove()