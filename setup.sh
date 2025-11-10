#!/bin/bash

# ============================================================================
# SCRIPT DE INSTALACIÓN Y CONFIGURACIÓN
# Sistema de Gestión de Valores Cotizados
# ============================================================================

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================================
# VERIFICACIÓN DE REQUISITOS
# ============================================================================

check_requirements() {
    print_header "Verificando Requisitos del Sistema"
    
    local all_ok=true
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 instalado (versión $PYTHON_VERSION)"
    else
        print_error "Python 3 no está instalado"
        all_ok=false
    fi
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 instalado"
    else
        print_error "pip3 no está instalado"
        all_ok=false
    fi
    
    # Verificar PostgreSQL
    if command -v psql &> /dev/null; then
        PSQL_VERSION=$(psql --version | cut -d' ' -f3)
        print_success "PostgreSQL instalado (versión $PSQL_VERSION)"
    else
        print_warning "PostgreSQL no está instalado o no está en el PATH"
        print_info "Asegúrate de tener PostgreSQL instalado y corriendo"
    fi
    
    # Verificar pg_dump (para backups)
    if command -v pg_dump &> /dev/null; then
        print_success "pg_dump disponible"
    else
        print_warning "pg_dump no encontrado (necesario para backups)"
    fi
    
    if [ "$all_ok" = false ]; then
        print_error "Algunos requisitos no están cumplidos"
        exit 1
    fi
}

# ============================================================================
# CREACIÓN DE ENTORNO VIRTUAL
# ============================================================================

setup_virtualenv() {
    print_header "Configurando Entorno Virtual"
    
    if [ -d "venv" ]; then
        print_warning "El directorio venv ya existe"
        read -p "¿Deseas eliminarlo y crear uno nuevo? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            rm -rf venv
            print_info "Directorio venv eliminado"
        else
            print_info "Usando entorno virtual existente"
            return
        fi
    fi
    
    print_info "Creando entorno virtual..."
    python3 -m venv venv
    print_success "Entorno virtual creado"
    
    # Activar entorno virtual
    source venv/bin/activate
    print_success "Entorno virtual activado"
}

# ============================================================================
# INSTALACIÓN DE DEPENDENCIAS
# ============================================================================

install_dependencies() {
    print_header "Instalando Dependencias de Python"
    
    # Actualizar pip
    print_info "Actualizando pip..."
    pip install --upgrade pip
    
    # Instalar dependencias
    print_info "Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
    
    print_success "Dependencias instaladas correctamente"
}

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

setup_database() {
    print_header "Configuración de Base de Datos"
    
    # Verificar si existe el archivo .env
    if [ ! -f ".env" ]; then
        print_info "Creando archivo .env desde .env.example..."
        cp .env.example .env
        print_success "Archivo .env creado"
        print_warning "Por favor, edita el archivo .env con tus credenciales de PostgreSQL"
        
        read -p "¿Deseas editar el archivo .env ahora? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        print_success "Archivo .env ya existe"
    fi
    
    # Preguntar si crear la base de datos
    print_info "La base de datos debe ser creada manualmente"
    print_info "Comandos necesarios:"
    echo "  1. Conectar a PostgreSQL: psql -U postgres"
    echo "  2. Crear base de datos: CREATE DATABASE stock_management;"
    echo "  3. Ejecutar script SQL: \\i init_database.sql"
    echo "  O desde terminal: psql -U postgres -d stock_management -f init_database.sql"
    
    read -p "¿La base de datos ya está creada? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_success "Base de datos lista"
        return
    fi
    
    read -p "¿Deseas intentar crear la base de datos ahora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_info "Creando base de datos..."
        
        # Leer credenciales del .env
        if [ -f ".env" ]; then
            export $(cat .env | grep -v '^#' | xargs)
        fi
        
        # Intentar crear la base de datos
        createdb -U ${DB_USER:-postgres} -h ${DB_HOST:-localhost} stock_management 2>/dev/null || true
        
        # Ejecutar script SQL
        if [ -f "init_database.sql" ]; then
            psql -U ${DB_USER:-postgres} -h ${DB_HOST:-localhost} -d stock_management -f init_database.sql
            print_success "Base de datos inicializada"
        else
            print_error "Archivo init_database.sql no encontrado"
        fi
    fi
}

# ============================================================================
# PRUEBA DEL SISTEMA
# ============================================================================

test_system() {
    print_header "Probando el Sistema"
    
    if [ -f "test_connection.py" ]; then
        print_info "Ejecutando pruebas de conexión..."
        python test_connection.py
    else
        print_warning "Archivo test_connection.py no encontrado"
    fi
}

# ============================================================================
# CREACIÓN DE DIRECTORIOS
# ============================================================================

create_directories() {
    print_header "Creando Estructura de Directorios"
    
    mkdir -p logs
    mkdir -p backups
    mkdir -p exports
    
    print_success "Directorios creados"
}

# ============================================================================
# INFORMACIÓN FINAL
# ============================================================================

print_final_info() {
    print_header "¡Instalación Completada!"
    
    echo -e "${GREEN}El sistema está listo para usar.${NC}\n"
    
    echo "Para ejecutar la aplicación:"
    echo "  1. Activa el entorno virtual:"
    echo "     ${YELLOW}source venv/bin/activate${NC}"
    echo ""
    echo "  2. Ejecuta la aplicación:"
    echo "     ${YELLOW}streamlit run app.py${NC}"
    echo ""
    echo "  3. La aplicación se abrirá en:"
    echo "     ${BLUE}http://localhost:8501${NC}"
    echo ""
    
    echo "Comandos útiles:"
    echo "  - Crear backup:        ${YELLOW}python backup_database.py${NC}"
    echo "  - Listar backups:      ${YELLOW}python backup_database.py --list${NC}"
    echo "  - Probar conexión:     ${YELLOW}python test_connection.py${NC}"
    echo ""
    
    echo "Documentación completa en: ${BLUE}README.md${NC}"
    echo ""
}

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

main() {
    clear
    
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                    ║"
    echo "║     SISTEMA DE GESTIÓN DE VALORES COTIZADOS                       ║"
    echo "║     Instalación y Configuración                                   ║"
    echo "║                                                                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    # Ejecutar pasos de instalación
    check_requirements
    setup_virtualenv
    install_dependencies
    create_directories
    setup_database
    
    # Preguntar si ejecutar pruebas
    read -p "¿Deseas ejecutar las pruebas del sistema ahora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        test_system
    fi
    
    print_final_info
}

# Ejecutar función principal
main