#!/bin/bash

# ============================================================================
# SCRIPT DE STARTUP - BolsaV1 Sistema de Gestão de Valores Cotizados
# ============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Banner de bienvenida
echo -e "${PURPLE}"
echo "============================================================================"
echo "🚀 BolsaV1 - Sistema de Gestão de Valores Cotizados"
echo "============================================================================"
echo -e "${NC}"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Uso:${NC}"
    echo "  $0 [COMANDO]"
    echo ""
    echo -e "${BLUE}Comandos disponibles:${NC}"
    echo "  start       - Iniciar todos los servicios"
    echo "  stop        - Detener todos los servicios"
    echo "  restart     - Reiniciar todos los servicios"
    echo "  logs        - Mostrar logs en tiempo real"
    echo "  status      - Mostrar estado de los servicios"
    echo "  build       - Construir/reconstruir imágenes"
    echo "  clean       - Limpiar containers y volumes"
    echo "  admin       - Iniciar con PgAdmin incluido"
    echo "  backup      - Crear backup de la base de datos"
    echo "  restore     - Restaurar backup de la base de datos"
    echo "  shell       - Acceder al shell del contenedor de la app"
    echo "  psql        - Acceder a PostgreSQL directamente"
    echo "  help        - Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  $0 start     # Iniciar la aplicación"
    echo "  $0 admin     # Iniciar con administrador web de BD"
    echo "  $0 logs      # Ver logs en tiempo real"
    echo "  $0 backup    # Crear backup de datos"
    echo ""
}

# Función para verificar dependencias
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        echo "Instalar con: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose no está instalado${NC}"
        echo "Instalar con: https://docs.docker.com/compose/install/"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependencias verificadas${NC}"
}

# Función para iniciar servicios
start_services() {
    echo -e "${BLUE}🚀 Iniciando servicios...${NC}"
    check_dependencies
    
    # Crear directorios necesarios
    mkdir -p logs exports backups
    
    # Iniciar servicios
    docker-compose up -d postgres bolsa_app
    
    echo -e "${GREEN}✅ Servicios iniciados${NC}"
    echo -e "${BLUE}📱 Aplicación disponible en: http://localhost:8501${NC}"
    echo -e "${YELLOW}⏳ Espera 30-60 segundos para que se complete la inicialización...${NC}"
}

# Función para iniciar con admin
start_with_admin() {
    echo -e "${BLUE}🚀 Iniciando servicios con PgAdmin...${NC}"
    check_dependencies
    
    mkdir -p logs exports backups
    
    # Iniciar todos los servicios incluyendo PgAdmin
    docker-compose --profile admin up -d
    
    echo -e "${GREEN}✅ Servicios iniciados con PgAdmin${NC}"
    echo -e "${BLUE}📱 Aplicación: http://localhost:8501${NC}"
    echo -e "${BLUE}🗄️  PgAdmin: http://localhost:8080${NC}"
    echo -e "${YELLOW}   Usuario: admin@bolsa.com${NC}"
    echo -e "${YELLOW}   Contraseña: admin_bolsa_2025${NC}"
}

# Función para detener servicios
stop_services() {
    echo -e "${BLUE}🛑 Deteniendo servicios...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para reiniciar
restart_services() {
    echo -e "${BLUE}🔄 Reiniciando servicios...${NC}"
    stop_services
    sleep 2
    start_services
}

# Función para mostrar logs
show_logs() {
    echo -e "${BLUE}📋 Mostrando logs (Ctrl+C para salir)...${NC}"
    docker-compose logs -f
}

# Función para mostrar estado
show_status() {
    echo -e "${BLUE}📊 Estado de los servicios:${NC}"
    docker-compose ps
    echo ""
    echo -e "${BLUE}📈 Uso de recursos:${NC}"
    docker stats $(docker-compose ps -q) --no-stream
}

# Función para build
build_services() {
    echo -e "${BLUE}🔨 Construyendo imágenes...${NC}"
    docker-compose build --no-cache
    echo -e "${GREEN}✅ Imágenes construidas${NC}"
}

# Función para limpiar
clean_services() {
    echo -e "${YELLOW}⚠️  Esta operación eliminará todos los containers y volumes${NC}"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🧹 Limpiando containers y volumes...${NC}"
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ Limpieza completada${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Función para backup
backup_database() {
    echo -e "${BLUE}💾 Creando backup de la base de datos...${NC}"
    
    # Verificar que postgres esté corriendo
    if ! docker-compose ps postgres | grep -q "Up"; then
        echo -e "${RED}❌ PostgreSQL no está corriendo${NC}"
        exit 1
    fi
    
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
    
    docker-compose exec postgres pg_dump -U bolsa_user -d stock_management > "$BACKUP_FILE"
    
    echo -e "${GREEN}✅ Backup creado: $BACKUP_FILE${NC}"
}

# Función para restore
restore_database() {
    echo -e "${BLUE}📥 Restaurando backup de base de datos...${NC}"
    
    if [ ! -f "$1" ]; then
        echo -e "${RED}❌ Archivo de backup no encontrado: $1${NC}"
        echo -e "${YELLOW}Uso: $0 restore <archivo_backup.sql>${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}⚠️  Esta operación sobrescribirá la base de datos actual${NC}"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec -T postgres psql -U bolsa_user -d stock_management < "$1"
        echo -e "${GREEN}✅ Backup restaurado${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Función para shell
open_shell() {
    echo -e "${BLUE}🐚 Abriendo shell en el contenedor de la aplicación...${NC}"
    docker-compose exec bolsa_app /bin/bash
}

# Función para psql
open_psql() {
    echo -e "${BLUE}🗄️  Conectando a PostgreSQL...${NC}"
    docker-compose exec postgres psql -U bolsa_user -d stock_management
}

# Procesar argumentos
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    build)
        build_services
        ;;
    clean)
        clean_services
        ;;
    admin)
        start_with_admin
        ;;
    backup)
        backup_database
        ;;
    restore)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Especifica el archivo de backup${NC}"
            echo -e "${YELLOW}Uso: $0 restore <archivo_backup.sql>${NC}"
            exit 1
        fi
        restore_database "$2"
        ;;
    shell)
        open_shell
        ;;
    psql)
        open_psql
        ;;
    help|*)
        show_help
        ;;
esac