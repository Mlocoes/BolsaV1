# 🐳 GUÍA DOCKER - BolsaV1
## Sistema de Gestão de Valores Cotizados

---

**📅 Última actualización:** 10 de novembro de 2025  
**🎯 Versión:** BolsaV1 - Fase 0 (Dockerizado)  
**🐳 Docker:** Pronto para producción  

---

## 🎯 INTRODUCCIÓN

Esta guía te permite ejecutar **BolsaV1** usando Docker, sin necesidad de instalar PostgreSQL, Python o dependencias localmente. Todo se ejecuta en contenedores aislados.

### 🏆 Beneficios de la versión Docker:
- ✅ **Instalación instantánea** (un solo comando)
- ✅ **Sin dependencias locales** (solo Docker)  
- ✅ **Entorno aislado** y reproducible
- ✅ **Base de datos incluida** (PostgreSQL)
- ✅ **Backup/Restore automatizado**
- ✅ **Escalable** para múltiples instancias

---

## 📋 REQUISITOS

### **Únicos requisitos del sistema:**
1. **Docker** (>= 20.10)
2. **Docker Compose** (>= 2.0)

### **Instalación de Docker:**

#### **Ubuntu/Debian:**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin

# Reiniciar para aplicar permisos
newgrp docker
```

#### **Windows:**
- Descargar **Docker Desktop** desde: https://www.docker.com/products/docker-desktop

#### **macOS:**
- Descargar **Docker Desktop** desde: https://www.docker.com/products/docker-desktop

---

## 🚀 INICIO RÁPIDO

### **1. Clonar/Descargar proyecto**
```bash
cd ~/Escritorio
# Si tienes git: git clone [repo-url] BolsaV1
# O simplemente asegúrate de tener todos los archivos en la carpeta
```

### **2. Iniciar aplicación**
```bash
cd BolsaV1
./startup.sh start
```

### **3. Acceder a la aplicación**
- **Aplicación principal:** http://localhost:8501
- **Esperar 30-60 segundos** para la inicialización completa

¡Y listo! El sistema estará funcionando con base de datos incluida.

---

## 🎮 COMANDOS PRINCIPALES

El script `startup.sh` simplifica todas las operaciones:

```bash
# Comandos básicos
./startup.sh start      # Iniciar servicios
./startup.sh stop       # Detener servicios  
./startup.sh restart    # Reiniciar servicios
./startup.sh status     # Ver estado de servicios
./startup.sh logs       # Ver logs en tiempo real

# Comandos avanzados
./startup.sh admin      # Iniciar con administrador web de BD
./startup.sh build      # Reconstruir imágenes
./startup.sh clean      # Limpiar todo (⚠️ elimina datos)

# Administración de datos
./startup.sh backup     # Crear backup de BD
./startup.sh restore archivo.sql  # Restaurar backup

# Debugging
./startup.sh shell      # Acceder al contenedor
./startup.sh psql       # Conectar a PostgreSQL directamente
```

---

## 🗄️ GESTIÓN DE BASE DE DATOS

### **Acceso Directo a PostgreSQL**
```bash
# Conectar a la BD
./startup.sh psql

# Dentro de psql:
\dt                     # Ver tablas
SELECT * FROM ativos;   # Ver activos
\q                      # Salir
```

### **Administrador Web (PgAdmin)**
```bash
# Iniciar con interfaz web de administración
./startup.sh admin

# Acceder a: http://localhost:8080
# Usuario: admin@bolsa.com  
# Contraseña: admin_bolsa_2025

# Configurar conexión en PgAdmin:
# Host: postgres
# Puerto: 5432
# Base de datos: stock_management
# Usuario: bolsa_user
# Contraseña: bolsa_password_2025
```

### **Backups y Restauración**
```bash
# Crear backup automático
./startup.sh backup

# El archivo se guarda en: backups/backup_YYYYMMDD_HHMMSS.sql

# Restaurar desde backup
./startup.sh restore backups/backup_20251110_143022.sql
```

---

## 📊 ARQUITECTURA DE SERVICIOS

### **Servicios incluidos:**

#### **1. PostgreSQL Database** (`postgres`)
- **Puerto:** 5432
- **Base de datos:** stock_management  
- **Usuario:** bolsa_user
- **Volumen persistente:** `postgres_data`

#### **2. Streamlit App** (`bolsa_app`)
- **Puerto:** 8501
- **Build:** Dockerfile local
- **Volúmenes montados:** logs, exports, backups

#### **3. PgAdmin** (`pgadmin`) - Opcional
- **Puerto:** 8080  
- **Activación:** `./startup.sh admin`
- **Volumen persistente:** `pgadmin_data`

### **Red Docker:**
- **Red:** `bolsa_network`
- **Comunicación:** Los servicios se comunican por nombres de contenedor

### **Volúmenes persistentes:**
```bash
# Listar volúmenes
docker volume ls | grep bolsa

# Inspeccionar volumen
docker volume inspect bolsa_postgres_data
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
BolsaV1/
├── 🐳 DOCKER FILES
│   ├── Dockerfile              # Imagen de la aplicación
│   ├── docker-compose.yml      # Orquestación de servicios
│   ├── .env.docker            # Variables de entorno para Docker
│   ├── init-db.sql            # Script de inicialización de BD
│   └── startup.sh             # Script de administración
├── 📱 APPLICATION
│   ├── app.py                 # Aplicación principal
│   ├── requirements.txt       # Dependencias Python
│   └── .env                   # Config local (no usado en Docker)
├── 📊 DATA & LOGS
│   ├── logs/                  # Logs de aplicación
│   ├── exports/               # Archivos exportados
│   └── backups/               # Backups de BD
└── 📖 DOCUMENTATION
    ├── README.md              # Documentación principal
    ├── README-DOCKER.md       # Esta guía
    ├── RELATORIO.md           # Plan de implementación
    └── FASE1_IMPLEMENTADA.md  # Mejoras implementadas
```

---

## 🔧 CONFIGURACIÓN AVANZADA

### **Variables de Entorno**

Editar `.env.docker` para configurar:

```bash
# Base de datos
DATABASE_URL=postgresql://usuario:password@postgres:5432/bd

# Logging
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR

# Yahoo Finance
YF_TIMEOUT=10

# Streamlit
STREAMLIT_SERVER_PORT=8501
```

### **Puertos Personalizados**

Modificar `docker-compose.yml`:

```yaml
services:
  bolsa_app:
    ports:
      - "8502:8501"  # Cambiar puerto externo
  postgres:
    ports:
      - "5433:5432"  # Cambiar puerto de PostgreSQL
```

### **Recursos del Sistema**

Limitar recursos en `docker-compose.yml`:

```yaml
services:
  bolsa_app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

---

## 🔍 TROUBLESHOOTING

### **Problemas Comunes:**

#### **🐳 "docker: command not found"**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### **🔒 "permission denied while trying to connect to Docker"**
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

#### **⏳ "La aplicación no carga"**
```bash
# Verificar estado de servicios
./startup.sh status

# Ver logs para debugging
./startup.sh logs

# Reiniciar servicios
./startup.sh restart
```

#### **🗄️ "Error de conexión a BD"**
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Verificar logs de BD
docker-compose logs postgres

# Recrear servicios
./startup.sh clean
./startup.sh start
```

#### **💾 "Error en el puerto 8501"**
```bash
# Verificar qué proceso usa el puerto
lsof -i :8501
sudo netstat -tlnp | grep 8501

# Cambiar puerto en docker-compose.yml si es necesario
```

### **Logs Detallados:**

```bash
# Ver logs de servicio específico
docker-compose logs postgres
docker-compose logs bolsa_app

# Seguir logs en tiempo real
docker-compose logs -f bolsa_app

# Ver logs con timestamp
docker-compose logs -t bolsa_app
```

---

## 🔒 SEGURIDAD

### **Para Desarrollo:**
- ✅ Contraseñas por defecto incluidas
- ✅ Puerto PostgreSQL expuesto para debugging
- ✅ PgAdmin disponible opcionalmente

### **Para Producción:**

#### **1. Cambiar credenciales:**
```bash
# En .env.docker
DATABASE_URL=postgresql://user_prod:password_segura@postgres:5432/stock_management

# En docker-compose.yml  
POSTGRES_USER: user_prod
POSTGRES_PASSWORD: password_segura_larga
```

#### **2. Usar Docker Secrets:**
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
services:
  postgres:
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
```

#### **3. Cerrar puertos innecesarios:**
```yaml
services:
  postgres:
    # Comentar ports para que no sea accesible externamente
    # ports:
    #   - "5432:5432"
```

#### **4. Usar reverse proxy:**
```bash
# Instalar nginx o traefik para SSL/TLS
# Configurar dominio propio
# Certificados Let's Encrypt
```

---

## 📈 MONITOREO Y LOGS

### **Monitoreo de Recursos:**
```bash
# Uso de recursos en tiempo real
docker stats

# Uso por servicio
./startup.sh status

# Inspeccionar contenedores
docker-compose exec bolsa_app top
docker-compose exec postgres top
```

### **Logs de Aplicación:**
```bash
# Logs dentro del contenedor
docker-compose exec bolsa_app tail -f /app/logs/bolsa_v1.log

# Logs de Streamlit
docker-compose logs -f bolsa_app

# Logs de PostgreSQL  
docker-compose logs -f postgres
```

---

## 🚀 DESPLIEGUE EN PRODUCCIÓN

### **Servidor VPS/Cloud:**

#### **1. Preparar servidor:**
```bash
# Conectar al servidor
ssh usuario@tu-servidor.com

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Transferir archivos
scp -r BolsaV1/ usuario@tu-servidor.com:~/
```

#### **2. Configurar producción:**
```bash
# En el servidor
cd BolsaV1

# Editar configuraciones para producción
nano .env.docker
nano docker-compose.yml

# Iniciar servicios
./startup.sh start
```

#### **3. Configurar dominio (opcional):**
```bash
# Instalar nginx
sudo apt install nginx

# Configurar reverse proxy
sudo nano /etc/nginx/sites-available/bolsa

# Contenido ejemplo:
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Activar sitio
sudo ln -s /etc/nginx/sites-available/bolsa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📋 COMANDOS DE REFERENCIA RÁPIDA

```bash
# GESTIÓN BÁSICA
./startup.sh start                    # Iniciar
./startup.sh stop                     # Detener  
./startup.sh restart                  # Reiniciar
./startup.sh status                   # Estado

# ADMINISTRACIÓN
./startup.sh admin                    # Con PgAdmin
./startup.sh logs                     # Ver logs
./startup.sh shell                    # Shell de app
./startup.sh psql                     # PostgreSQL CLI

# DATOS
./startup.sh backup                   # Backup BD
./startup.sh restore archivo.sql      # Restaurar BD

# DESARROLLO  
./startup.sh build                    # Rebuild imágenes
./startup.sh clean                    # Limpiar todo

# DOCKER DIRECTO
docker-compose ps                     # Lista servicios
docker-compose logs -f                # Todos los logs
docker-compose exec bolsa_app bash    # Shell de app
docker-compose exec postgres psql -U bolsa_user stock_management
```

---

## 🎉 CONCLUSIÓN

Con esta configuración Docker, **BolsaV1** es:

- ✅ **Fácil de instalar** (un comando)
- ✅ **Portable** (funciona igual en cualquier sistema)
- ✅ **Escalable** (múltiples instancias)
- ✅ **Mantenible** (backups automatizados)
- ✅ **Seguro** (entorno aislado)

La **Fase 0 (Dockerización)** está completa y lista para producción.

---

**📧 Soporte:** Si encuentras problemas, revisa la sección de troubleshooting o verifica los logs con `./startup.sh logs`

**🔄 Próximos pasos:** Con Docker funcionando, puedes proceder con las siguientes fases del plan de implementación (Fase 2: Refactorización, Fase 3: Autenticación, etc.)

---

**📅 Documentación generada:** 10 de novembro de 2025  
**🏷️ Versión:** BolsaV1 - Dockerizado  
**🐳 Docker:** Completamente configurado  
**🎯 Estado:** Listo para uso en producción