#!/usr/bin/env python3
"""
Migración Simplificada FASE 3 - BolsaV1
Creación directa usando SQLAlchemy
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.models.base import Base, engine
from app.services.auth_service import AuthService


def main():
    """Migración simplificada usando SQLAlchemy"""
    print("=" * 60)
    print("🚀 MIGRACIÓN SIMPLIFICADA FASE 3 - BolsaV1 v3.0.0")
    print("🔐 Sistema de Autenticación y Multi-tenant")
    print("=" * 60)
    
    # Verificar conexión
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a base de datos OK")
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return False
    
    try:
        print("\n🔄 Creando todas las tablas...")
        
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
        
        print("\n👤 Creando usuario administrador...")
        
        # Crear usuario admin directamente
        from app.models import User
        import hashlib
        
        session = engine.connect()
        with engine.begin() as conn:
            # Verificar si ya existe admin
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE username = 'admin'"))
            if result.scalar() > 0:
                print("ℹ️ Usuario admin ya existe")
            else:
                # Crear admin con hash simple (temporal)
                simple_hash = hashlib.sha256("admin123".encode()).hexdigest()
                conn.execute(text("""
                    INSERT INTO users (username, email, hashed_password, full_name, is_active, is_admin, created_at)
                    VALUES ('admin', 'admin@bolsav1.com', :password, 'Administrador Sistema', true, true, :created_at)
                """), {"password": simple_hash, "created_at": datetime.now()})
                print("✅ Usuario admin creado: admin / admin123")
                print("📧 Email: admin@bolsav1.com")
        
        print("\n👥 Creando usuarios de ejemplo...")
        
        # Usuario demo usando AuthService  
        success, message, demo_user = AuthService.register_user(
            username="demo_user",
            email="demo@bolsav1.com",
            password="demo123456",
            full_name="Usuario Demo"
        )
        
        if success:
            print(f"✅ Usuario demo: demo_user / demo123456")
        else:
            print(f"ℹ️ Demo: {message}")
        
        # Usuario investor
        success, message, inv_user = AuthService.register_user(
            username="investor1",
            email="investor@bolsav1.com", 
            password="invest123",
            full_name="Inversor Ejemplo"
        )
        
        if success:
            print(f"✅ Usuario investor: investor1 / invest123")
        else:
            print(f"ℹ️ Investor: {message}")
        
        print("\n🔍 Verificación final...")
        
        # Verificar usuarios creados
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"📊 Usuarios totales: {user_count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_admin = true"))
            admin_count = result.scalar()
            print(f"🔐 Usuarios admin: {admin_count}")
        
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("🔐 Sistema multi-usuario activado")
        print("🚀 BolsaV1 v3.0.0 listo para usar")
        print("=" * 60)
        
        print("\n📋 CREDENCIALES DE ACCESO:")
        print("👨‍💼 Admin: admin / admin123")
        print("🧪 Demo:  demo_user / demo123456") 
        print("💼 Test:  investor1 / invest123")
        print("\n⚠️ ¡Cambiar contraseñas en producción!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)