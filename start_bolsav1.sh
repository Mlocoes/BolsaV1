#!/bin/bash

# ===================================================================
# SCRIPT DE INICIO BOLSAV1 v3.0.0
# Sistema Multi-Usuario de Gestión de Activos Financieros
# ===================================================================

echo "🚀 Iniciando BolsaV1 v3.0.0..."
echo "🔐 Sistema Multi-Usuario Activado"
echo ""

# Configuración
PROJECT_DIR="/home/mloco/Escritorio/BolsaV1"
PORT=8500
DATABASE_URL="postgresql://bolsa_user:bolsa_password_2025@localhost:5432/stock_management"

# Verificar que el directorio existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Directorio del proyecto no encontrado: $PROJECT_DIR"
    exit 1
fi

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR"

# Activar entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Error: Entorno virtual no encontrado. Ejecuta: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Verificar que PostgreSQL esté corriendo
echo "🔍 Verificando base de datos..."
if ! docker ps | grep -q "bolsa_postgres"; then
    echo "⚠️ PostgreSQL no está corriendo. Iniciando..."
    docker-compose up -d postgres
    sleep 5
fi

# Verificar conexión a la base de datos
echo "🔌 Verificando conexión a la base de datos..."
if ! python3 -c "from app.models.base import engine; from sqlalchemy import text; engine.execute(text('SELECT 1'))" 2>/dev/null; then
    echo "❌ Error: No se puede conectar a la base de datos"
    echo "🔧 Verifica que PostgreSQL esté corriendo en Docker"
    exit 1
fi

echo "✅ Base de datos conectada correctamente"

# Detener procesos anteriores en el mismo puerto
echo "🧹 Limpiando procesos anteriores..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

# Iniciar la aplicación
echo ""
echo "🎯 Iniciando BolsaV1 en puerto $PORT..."
echo "🌐 URL de acceso: http://localhost:$PORT"
echo "👤 Credenciales: admin / admin123"
echo ""
echo "📋 Para detener la aplicación presiona Ctrl+C"
echo ""

# Ejecutar Streamlit
DATABASE_URL="$DATABASE_URL" streamlit run main.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --browser.gatherUsageStats=false \
    --theme.primaryColor="#1f77b4" \
    --theme.backgroundColor="#ffffff" \
    --theme.secondaryBackgroundColor="#f0f2f6"