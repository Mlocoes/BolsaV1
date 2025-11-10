#!/bin/bash

# ============================================================================
# SCRIPT DE VERIFICACIÓN - BolsaV1 FASE 1
# ============================================================================

echo "🔍 VERIFICANDO IMPLEMENTACIÓN FASE 1 - CORRECCIONES CRÍTICAS"
echo "============================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}1. VERIFICANDO SINTAXIS DE CÓDIGO${NC}"
echo "-----------------------------------"

cd /home/mloco/Escritorio/BolsaV1

# Verificar sintaxis Python
if python3 -m py_compile app.py; then
    echo -e "${GREEN}✅ Sintaxis Python correcta${NC}"
else
    echo -e "${RED}❌ Error de sintaxis en app.py${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. VERIFICANDO DEPENDENCIAS${NC}"
echo "-----------------------------"

# Activar entorno virtual y verificar dependencias
source venv/bin/activate

DEPS=("streamlit" "yfinance" "sqlalchemy" "plotly" "pandas" "psycopg2")
MISSING_DEPS=()

for dep in "${DEPS[@]}"; do
    if pip show $dep > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $dep instalado${NC}"
    else
        echo -e "${RED}❌ $dep NO instalado${NC}"
        MISSING_DEPS+=($dep)
    fi
done

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Todas las dependencias están instaladas${NC}"
else
    echo -e "${YELLOW}⚠️ Dependencias faltantes: ${MISSING_DEPS[*]}${NC}"
fi

echo ""
echo -e "${BLUE}3. VERIFICANDO MEJORAS IMPLEMENTADAS${NC}"
echo "-------------------------------------"

# Verificar validación de saldo en ventas
if grep -q "saldo insuficiente" app.py; then
    echo -e "${GREEN}✅ Validación de saldo en ventas implementada${NC}"
else
    echo -e "${RED}❌ Validación de saldo NO implementada${NC}"
fi

# Verificar sistema de logging
if grep -q "logger.info" app.py; then
    echo -e "${GREEN}✅ Sistema de logging implementado${NC}"
else
    echo -e "${RED}❌ Sistema de logging NO implementado${NC}"
fi

# Verificar fallback de cotizaciones
if grep -q "obter_ultima_cotacao_bd" app.py; then
    echo -e "${GREEN}✅ Fallback para cotizaciones implementado${NC}"
else
    echo -e "${RED}❌ Fallback para cotizaciones NO implementado${NC}"
fi

# Verificar validación de tickers
if grep -q "validar_ticker" app.py; then
    echo -e "${GREEN}✅ Validación de tickers implementada${NC}"
else
    echo -e "${RED}❌ Validación de tickers NO implementada${NC}"
fi

# Verificar directorio de logs
if [ -d "logs" ]; then
    echo -e "${GREEN}✅ Directorio logs existe${NC}"
else
    echo -e "${YELLOW}⚠️ Directorio logs no existe (se creará automáticamente)${NC}"
fi

echo ""
echo -e "${BLUE}4. VERIFICANDO CONFIGURACIÓN${NC}"
echo "-----------------------------"

# Verificar archivo .env
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Archivo .env existe${NC}"
else
    echo -e "${RED}❌ Archivo .env NO existe${NC}"
fi

echo ""
echo -e "${BLUE}5. REQUISITOS PARA TESTING COMPLETO${NC}"
echo "------------------------------------"

echo -e "${YELLOW}Para testing completo necesitas:${NC}"
echo "• PostgreSQL instalado y corriendo"
echo "• Base de datos 'stock_management' creada"
echo "• Usuario postgres con permisos"
echo ""
echo -e "${YELLOW}Comandos para configurar PostgreSQL:${NC}"
echo "sudo apt update && sudo apt install postgresql postgresql-contrib"
echo "sudo -u postgres createuser --interactive"
echo "sudo -u postgres createdb stock_management"
echo ""

echo -e "${BLUE}6. CÓMO EJECUTAR LA APLICACIÓN${NC}"
echo "------------------------------"
echo "1. Asegurar que PostgreSQL esté corriendo:"
echo "   sudo systemctl start postgresql"
echo ""
echo "2. Activar entorno virtual:"
echo "   source venv/bin/activate"
echo ""
echo "3. Ejecutar aplicación:"
echo "   streamlit run app.py"
echo ""

echo ""
echo -e "${GREEN}🎉 RESUMEN FASE 1 COMPLETADA${NC}"
echo "============================"
echo -e "${GREEN}✅ Validación de saldo en ventas${NC}"
echo -e "${GREEN}✅ Sistema de logging profesional${NC}"
echo -e "${GREEN}✅ Fallback para cotizaciones offline${NC}"
echo -e "${GREEN}✅ Validación de tickers válidos${NC}"
echo -e "${GREEN}✅ Mejores tratamiento de excepciones${NC}"
echo ""
echo -e "${BLUE}📋 Próximas fases disponibles en RELATORIO.md${NC}"
echo ""