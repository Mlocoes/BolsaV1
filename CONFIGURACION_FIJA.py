# ===================================================================
# CONFIGURACIÓN FIJA DE BOLSAV1 v3.0.0
# ===================================================================

# 🌐 ACCESO PERMANENTE AL SISTEMA
URL_FIJA = "http://localhost:8500"
PUERTO_FIJO = 8500

# 🔐 CREDENCIALES DE ACCESO
USUARIO_ADMIN = "admin"
PASSWORD_ADMIN = "admin123"
EMAIL_ADMIN = "admin@bolsav1.com"

# 🗄️ BASE DE DATOS
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "stock_management"
DB_USER = "bolsa_user"
DB_PASSWORD = "bolsa_password_2025"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 📋 INSTRUCCIONES DE USO:
# 
# 1. INICIAR EL SISTEMA:
#    ./start_bolsav1.sh
# 
# 2. ACCEDER AL SISTEMA:
#    http://localhost:8500
# 
# 3. CREDENCIALES:
#    Usuario: admin
#    Contraseña: admin123
# 
# 4. DETENER EL SISTEMA:
#    Ctrl+C en la terminal
#
# ===================================================================