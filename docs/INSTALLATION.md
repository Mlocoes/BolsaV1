# 🚀 Guía de Instalación y Configuración - BolsaV1

Esta guía te llevará paso a paso para instalar y configurar BolsaV1 en tu sistema.

---

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **RAM**: 4GB mínimo, 8GB recomendado
- **Almacenamiento**: 2GB espacio libre
- **Python**: 3.12 o superior
- **Docker**: 20.10+ con Docker Compose

### Software Requerido

1. **Python 3.12+**
   ```bash
   # Verificar versión
   python3 --version
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.12 python3.12-venv python3.12-dev
   
   # macOS
   brew install python@3.12
   
   # Windows: Descargar desde python.org
   ```

2. **Docker & Docker Compose**
   ```bash
   # Linux
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   
   # macOS: Instalar Docker Desktop
   # Windows: Instalar Docker Desktop
   
   # Verificar instalación
   docker --version
   docker-compose --version
   ```

3. **Git** (opcional pero recomendado)
   ```bash
   # Ubuntu/Debian
   sudo apt install git
   
   # macOS
   brew install git
   
   # Windows: Descargar desde git-scm.com
   ```

---

## 📥 Métodos de Instalación

### Opción 1: Docker (Recomendado)

Esta es la forma más rápida y segura de ejecutar BolsaV1.

#### 1. Descargar el Proyecto

```bash
# Si tienes git instalado
git clone https://github.com/tu-usuario/BolsaV1.git
cd BolsaV1

# O descargar ZIP desde GitHub y extraer
```

#### 2. Configurar Variables de Entorno

```bash
# Crear archivo de configuración
cp .env.example .env

# Editar configuración (opcional)
nano .env
```

#### 3. Ejecutar con Docker

```bash
# Iniciar servicios
docker-compose up -d

# Verificar que todo esté funcionando
docker-compose ps
```

#### 4. Acceder a la Aplicación

Abrir navegador y ir a: http://localhost:8501

### Opción 2: Instalación Manual

Para desarrolladores o instalaciones customizadas.

#### 1. Preparar Entorno Python

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Actualizar pip
pip install --upgrade pip
```

#### 2. Instalar Dependencias

```bash
# Instalar dependencias del proyecto
pip install -r requirements.txt
```

#### 3. Configurar Base de Datos

**Opción 3A: PostgreSQL con Docker**
```bash
# Ejecutar solo PostgreSQL
docker run --name postgres-bolsa \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=stock_management \
  -p 5432:5432 \
  -d postgres:15
```

**Opción 3B: PostgreSQL Local**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Crear base de datos
sudo -u postgres createdb stock_management
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

#### 4. Configurar Variables de Entorno

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/stock_management"
export LOG_LEVEL="INFO"
export CACHE_TIMEOUT="600"
```

#### 5. Ejecutar la Aplicación

```bash
# Activar entorno si no está activo
source venv/bin/activate

# Ejecutar aplicación
streamlit run main.py
```

---

## ⚙️ Configuración Detallada

### Variables de Entorno

Crear archivo `.env` en el directorio raíz:

```env
# Base de Datos
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/stock_management

# Logging
LOG_LEVEL=INFO

# Cache
CACHE_TIMEOUT=600

# API Rate Limiting
REQUEST_DELAY_MIN=2.0
REQUEST_DELAY_MAX=4.0

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Configuración Avanzada

#### PostgreSQL Tuning

Para mejor rendimiento, editar `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: stock_management
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres.conf:/etc/postgresql/postgresql.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

Crear `postgres.conf`:
```conf
# Optimizaciones básicas
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
max_connections = 100
```

#### Streamlit Configuration

Crear `.streamlit/config.toml`:
```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
```

---

## 🔧 Verificación de Instalación

### Tests Básicos

```bash
# 1. Verificar servicios Docker
docker-compose ps

# 2. Verificar conectividad PostgreSQL
docker-compose exec postgres psql -U postgres -d stock_management -c "SELECT version();"

# 3. Verificar logs de aplicación
docker-compose logs bolsa_app

# 4. Health Check manual
curl -f http://localhost:8501/_stcore/health || echo "App not responding"
```

### Tests Funcionales

1. **Abrir http://localhost:8501**
2. **Navegar a "Gestión de Valores"**
3. **Intentar agregar un activo de prueba: AAPL**
4. **Verificar que aparece en la lista**
5. **Navegar a "Cotizaciones" y verificar que carga datos**

---

## 🚨 Resolución de Problemas

### Problema 1: Docker no Inicia

**Error**: `Cannot connect to the Docker daemon`

**Solución**:
```bash
# Linux: Verificar que Docker esté corriendo
sudo systemctl status docker
sudo systemctl start docker

# Verificar permisos
sudo usermod -aG docker $USER
# Logout y login de nuevo
```

### Problema 2: Puerto 8501 en Uso

**Error**: `Port 8501 is already in use`

**Solución**:
```bash
# Encontrar proceso usando puerto
sudo lsof -i :8501

# Cambiar puerto en docker-compose.yml
services:
  bolsa_app:
    ports:
      - "8502:8501"  # Cambiar puerto externo
```

### Problema 3: PostgreSQL Connection Failed

**Error**: `could not connect to server`

**Solución**:
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps

# Verificar logs de PostgreSQL
docker-compose logs postgres

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

### Problema 4: Python Dependencies Issues

**Error**: `ModuleNotFoundError` o problemas de versiones

**Solución**:
```bash
# Recrear entorno virtual
deactivate  # Si estás en venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de nuevo
pip install --upgrade pip
pip install -r requirements.txt
```

### Problema 5: Yahoo Finance API Límites

**Error**: Cotizaciones no cargan o errores 429

**Solución**:
1. Verificar configuración de delays en `.env`
2. Aumentar `REQUEST_DELAY_MIN` y `REQUEST_DELAY_MAX`
3. Reducir frecuencia de consultas

### Problema 6: Permisos en Docker Volumes

**Error**: Permission denied al acceder a volúmenes

**Solución**:
```bash
# Linux: Dar permisos al directorio
sudo chown -R $USER:$USER ./data
sudo chmod -R 755 ./data

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

---

## 🔄 Actualizaciones

### Actualización con Docker

```bash
# 1. Parar servicios
docker-compose down

# 2. Actualizar código
git pull origin main

# 3. Reconstruir imágenes
docker-compose build --no-cache

# 4. Reiniciar servicios
docker-compose up -d
```

### Backup Antes de Actualizar

```bash
# Backup de base de datos
docker-compose exec postgres pg_dump -U postgres stock_management > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup de configuración
cp .env .env.backup
```

### Migración de Base de Datos

Si hay cambios en el esquema:

```bash
# Ejecutar migraciones (si están disponibles)
docker-compose exec bolsa_app python -c "
from app.models import create_tables
create_tables()
"
```

---

## 📊 Monitoreo y Mantenimiento

### Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs bolsa_app
docker-compose logs postgres

# Logs con timestamp
docker-compose logs -t bolsa_app
```

### Métricas Básicas

```bash
# Uso de recursos
docker stats

# Espacio usado por volúmenes
docker system df

# Limpiar recursos no usados
docker system prune -a
```

### Backup Automático

Crear script `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de base de datos
docker-compose exec -T postgres pg_dump -U postgres stock_management > $BACKUP_DIR/db_backup_$DATE.sql

# Backup de configuración
cp .env $BACKUP_DIR/env_backup_$DATE

# Limpiar backups antiguos (mantener últimos 7)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

Agregar a crontab:
```bash
# Backup diario a las 2 AM
0 2 * * * /path/to/BolsaV1/backup.sh
```

---

## 🌐 Configuración de Red

### Acceso Desde Otras Máquinas

Para acceder desde otras máquinas en la red local:

1. **Modificar docker-compose.yml**:
```yaml
services:
  bolsa_app:
    ports:
      - "0.0.0.0:8501:8501"  # Exponer en todas las interfaces
```

2. **Configurar firewall** (Linux):
```bash
sudo ufw allow 8501
```

3. **Acceder desde otra máquina**:
   - Obtener IP del servidor: `ip addr show`
   - Abrir: `http://IP_DEL_SERVIDOR:8501`

### HTTPS/SSL

Para producción con HTTPS:

1. **Usar nginx como reverse proxy**
2. **Obtener certificado SSL** (Let's Encrypt)
3. **Configurar redirección HTTP → HTTPS**

Ver documentación de deployment para configuración completa.

---

## 📞 Soporte

### Información del Sistema

Para reportar problemas, incluir esta información:

```bash
# Información del sistema
./debug_info.sh
```

Crear `debug_info.sh`:
```bash
#!/bin/bash
echo "=== BolsaV1 Debug Info ==="
echo "Date: $(date)"
echo "OS: $(uname -a)"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"
echo "Python: $(python3 --version)"
echo ""
echo "=== Docker Services ==="
docker-compose ps
echo ""
echo "=== Recent Logs ==="
docker-compose logs --tail=50 bolsa_app
```

### Recursos de Ayuda

- **GitHub Issues**: Para bugs y feature requests
- **Documentación**: `/docs/` en este repositorio
- **Logs**: Siempre incluir logs relevantes en reportes
- **Environment**: Incluir configuración (sin passwords)

---

**🎉 ¡Instalación Completa!**

Si todo salió bien, ya tienes BolsaV1 funcionando. Ve a la [Guía de Usuario](USER_GUIDE.md) para aprender a usar la aplicación.

*Para problemas específicos, crear issue en GitHub con información detallada del error.*