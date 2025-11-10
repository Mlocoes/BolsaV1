# ============================================================================
# ARCHIVO DE CONFIGURACIÓN DE ENTORNO
# Sistema de Gestión de Valores Cotizados
# ============================================================================
# 
# INSTRUCCIONES:
# 1. Copia este archivo como '.env' en la raíz del proyecto
# 2. Modifica los valores según tu configuración local
# 3. NO compartas el archivo .env con credenciales reales
# ============================================================================

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL
# ============================================================================

# Formato: postgresql://usuario:contraseña@host:puerto/nombre_base_datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stock_management

# Configuración detallada (alternativa)
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_management

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

# Entorno (development, production, testing)
ENVIRONMENT=development

# Puerto de la aplicación Streamlit (por defecto: 8501)
APP_PORT=8501

# ============================================================================
# CONFIGURACIÓN DE APIS EXTERNAS
# ============================================================================

# Yahoo Finance (yfinance no requiere API key, pero puedes configurar opciones)
# Timeout para peticiones (en segundos)
API_TIMEOUT=30

# Intervalo de actualización automática (en segundos)
AUTO_UPDATE_INTERVAL=300

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

# Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Archivo de log
LOG_FILE=logs/app.log

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

# Clave secreta para sesiones (genera una aleatoria en producción)
SECRET_KEY=tu_clave_secreta_aqui_cambiar_en_produccion

# ============================================================================
# CONFIGURACIÓN DE DATOS FINANCIEROS
# ============================================================================

# Días de histórico por defecto
DEFAULT_HISTORY_DAYS=30

# Moneda por defecto
DEFAULT_CURRENCY=USD

# Mercado por defecto
DEFAULT_MARKET=US

# ============================================================================
# CONFIGURACIÓN DE BACKUP (OPCIONAL)
# ============================================================================

# Directorio para backups
BACKUP_DIR=backups/

# Frecuencia de backup automático (en horas)
BACKUP_FREQUENCY=24

# ============================================================================
# NOTAS IMPORTANTES
# ============================================================================
#
# - Asegúrate de tener PostgreSQL instalado y corriendo
# - Crea la base de datos antes de ejecutar la aplicación:
#   $ createdb stock_management
#   O ejecuta el script SQL de inicialización
#
# - Para instalar dependencias:
#   $ pip install -r requirements.txt
#
# - Para ejecutar la aplicación:
#   $ streamlit run app.py
#
# ============================================================================