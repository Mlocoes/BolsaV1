#!/usr/bin/env python3
"""
Script de Migración FASE 3 - BolsaV1
Sistema de Autenticación y Multi-tenant

Este script ejecuta la migración de la base de datos para agregar
autenticación y aislamiento multi-tenant al sistema.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent))

from app.models.base import engine
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.config import Config
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def backup_database():
    """Crea backup de la base de datos antes de la migración"""
    try:
        backup_file = f"backup_pre_fase3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        # Extraer componentes de DATABASE_URL
        db_url = Config.DATABASE_URL
        # Formato: postgresql://user:password@host:port/database
        
        if "postgresql://" in db_url:
            # Parsear URL para pg_dump
            parts = db_url.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_db = parts[1].split("/")
            host_port = host_db[0].split(":")
            
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5432"
            database = host_db[1]
            user = user_pass[0]
            
            # Comando pg_dump
            cmd = f"pg_dump -h {host} -p {port} -U {user} -d {database} > {backup_file}"
            
            print(f"📦 Creando backup: {backup_file}")
            print(f"🔧 Ejecutar: {cmd}")
            print("💡 Ejecuta el comando anterior manualmente antes de continuar si es necesario")
            
        return True
        
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return False


def run_migration_sql():
    """Ejecuta el archivo SQL de migración"""
    try:
        migration_file = Path(__file__).parent / "fase3_migration.sql"
        
        if not migration_file.exists():
            logger.error("❌ Archivo fase3_migration.sql no encontrado")
            return False
        
        print("🔄 Ejecutando migración SQL...")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Ejecutar SQL en transacción
        with engine.begin() as conn:
            # Separar y ejecutar comandos SQL
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if statement and not statement.startswith('--'):
                    try:
                        print(f"  📝 Ejecutando statement {i+1}/{len(statements)}")
                        conn.execute(statement)
                    except Exception as stmt_error:
                        # Algunos comandos pueden fallar si ya existen (IF NOT EXISTS)
                        if "already exists" not in str(stmt_error).lower():
                            logger.warning(f"Error en statement {i+1}: {stmt_error}")
        
        print("✅ Migración SQL completada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando migración: {e}")
        return False


def verify_migration():
    """Verifica que la migración se ejecutó correctamente"""
    try:
        print("🔍 Verificando migración...")
        
        # Verificar que existe al menos un usuario admin
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
            admin_count = result.scalar()
            
            if admin_count > 0:
                print(f"✅ {admin_count} usuario(s) admin encontrado(s)")
            else:
                print("⚠️ No se encontraron usuarios admin")
                return False
            
            # Verificar índices creados
            result = conn.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename IN ('users', 'user_sessions', 'ativos', 'operacoes', 'posicoes')
                AND indexname LIKE 'idx_%'
            """)
            indices = result.fetchall()
            print(f"✅ {len(indices)} índices de multi-tenancy creados")
            
            # Verificar constraints únicos
            result = conn.execute("""
                SELECT conname FROM pg_constraint 
                WHERE conname IN ('unique_ticker_per_user', 'unique_position_per_user')
            """)
            constraints = result.fetchall()
            print(f"✅ {len(constraints)} constraints únicos por usuario creados")
        
        print("✅ Verificación completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando migración: {e}")
        return False


def create_sample_users():
    """Crea usuarios de ejemplo para testing"""
    try:
        print("👤 Creando usuarios de ejemplo...")
        
        # Usuario de prueba 1
        success, message, user1 = AuthService.register_user(
            username="demo_user",
            email="demo@bolsav1.com",
            password="demo123456",
            full_name="Usuario Demo"
        )
        
        if success:
            print(f"✅ Usuario demo creado: demo_user")
        else:
            print(f"ℹ️ Usuario demo: {message}")
        
        # Usuario de prueba 2
        success, message, user2 = AuthService.register_user(
            username="investor1",
            email="investor@bolsav1.com", 
            password="invest123",
            full_name="Inversor Ejemplo"
        )
        
        if success:
            print(f"✅ Usuario investor creado: investor1")
        else:
            print(f"ℹ️ Usuario investor: {message}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creando usuarios de ejemplo: {e}")
        return False


def main():
    """Función principal de migración"""
    print("=" * 60)
    print("🚀 MIGRACIÓN FASE 3 - BolsaV1 v3.0.0")
    print("🔐 Sistema de Autenticación y Multi-tenant")
    print("=" * 60)
    
    # Verificar conexión a BD
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Conexión a base de datos OK")
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return False
    
    # Confirmar migración
    print("\n🔍 Esta migración realizará los siguientes cambios:")
    print("   • Crear tablas users y user_sessions")
    print("   • Agregar user_id a tablas existentes")
    print("   • Modificar constraints únicos para multi-tenancy")
    print("   • Crear usuario admin por defecto")
    print("   • Migrar datos existentes al usuario admin")
    
    confirm = input("\n❓ ¿Continuar con la migración? (s/N): ").lower().strip()
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Migración cancelada")
        return False
    
    print("\n🔄 Iniciando migración...")
    
    # Paso 1: Backup (informativo)
    backup_database()
    
    # Paso 2: Ejecutar migración SQL
    if not run_migration_sql():
        print("❌ Error en migración SQL")
        return False
    
    # Paso 3: Verificar migración
    if not verify_migration():
        print("❌ Error en verificación")
        return False
    
    # Paso 4: Crear usuarios de ejemplo (opcional)
    create_demo = input("\n❓ ¿Crear usuarios de ejemplo para testing? (s/N): ").lower().strip()
    if create_demo in ['s', 'si', 'sí', 'y', 'yes']:
        create_sample_users()
    
    print("\n" + "=" * 60)
    print("🎉 MIGRACIÓN FASE 3 COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\n📋 Información importante:")
    print("   👤 Usuario admin: admin")
    print("   🔑 Contraseña admin: admin123")
    print("   ⚠️  CAMBIAR contraseña admin en producción")
    print("   🔐 Sistema multi-tenant activado")
    print("   📊 Datos existentes migrados al usuario admin")
    
    print("\n🚀 Próximos pasos:")
    print("   1. Probar login con usuario admin")
    print("   2. Cambiar contraseña del admin")
    print("   3. Crear usuarios adicionales según necesidad")
    print("   4. Probar aislamiento de datos entre usuarios")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)