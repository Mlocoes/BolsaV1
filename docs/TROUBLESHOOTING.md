# 🔧 Solución de Problemas - BolsaV1

Esta guía te ayudará a resolver los problemas más comunes que puedes encontrar al usar BolsaV1.

---

## 🚨 Problemas Comunes y Soluciones

### 🐳 Problemas de Docker

#### Error: "Cannot connect to the Docker daemon"

**Síntomas**:
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. 
Is the docker daemon running?
```

**Soluciones**:

1. **Verificar que Docker esté corriendo**:
   ```bash
   # Linux
   sudo systemctl status docker
   sudo systemctl start docker
   
   # macOS/Windows
   # Abrir Docker Desktop
   ```

2. **Verificar permisos**:
   ```bash
   # Linux - Agregar usuario al grupo docker
   sudo usermod -aG docker $USER
   # Logout y login nuevamente
   ```

3. **Reiniciar Docker**:
   ```bash
   # Linux
   sudo systemctl restart docker
   
   # macOS/Windows
   # Reiniciar Docker Desktop
   ```

#### Error: "Port 8501 is already in use"

**Síntomas**:
```
Error starting userland proxy: listen tcp 0.0.0.0:8501: 
bind: address already in use
```

**Soluciones**:

1. **Encontrar proceso usando el puerto**:
   ```bash
   sudo lsof -i :8501
   ```

2. **Terminar proceso existente**:
   ```bash
   sudo kill -9 <PID>
   ```

3. **Usar puerto diferente**:
   ```bash
   # Editar docker-compose.yml
   services:
     bolsa_app:
       ports:
         - "8502:8501"  # Cambiar puerto externo
   ```

#### Error: "No space left on device"

**Síntomas**:
```
Error response from daemon: write /var/lib/docker/tmp/...: 
no space left on device
```

**Soluciones**:

1. **Limpiar imágenes no usadas**:
   ```bash
   docker system prune -a
   ```

2. **Eliminar volúmenes no usados**:
   ```bash
   docker volume prune
   ```

3. **Verificar espacio disponible**:
   ```bash
   df -h
   docker system df
   ```

---

### 🗄️ Problemas de Base de Datos

#### Error: "could not connect to server"

**Síntomas**:
```
sqlalchemy.exc.OperationalError: could not connect to server: 
Connection refused
```

**Soluciones**:

1. **Verificar que PostgreSQL esté corriendo**:
   ```bash
   docker-compose ps
   docker-compose logs postgres
   ```

2. **Verificar configuración de conexión**:
   ```bash
   # Verificar variables de entorno
   echo $DATABASE_URL
   
   # Verificar .env
   cat .env | grep DATABASE_URL
   ```

3. **Reiniciar servicios de BD**:
   ```bash
   docker-compose restart postgres
   docker-compose logs -f postgres
   ```

4. **Probar conexión manual**:
   ```bash
   docker-compose exec postgres psql -U postgres -d stock_management -c "SELECT version();"
   ```

#### Error: "database does not exist"

**Síntomas**:
```
psql: FATAL: database "stock_management" does not exist
```

**Soluciones**:

1. **Recrear base de datos**:
   ```bash
   docker-compose down -v  # Elimina volúmenes
   docker-compose up -d    # Recrea todo
   ```

2. **Crear BD manualmente**:
   ```bash
   docker-compose exec postgres createdb -U postgres stock_management
   ```

#### Error: "password authentication failed"

**Síntomas**:
```
FATAL: password authentication failed for user "postgres"
```

**Soluciones**:

1. **Verificar credenciales en .env**:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/stock_management
   ```

2. **Reset de password**:
   ```bash
   docker-compose down
   docker volume rm bolsav1_postgres_data
   docker-compose up -d
   ```

---

### 📈 Problemas de Cotizaciones

#### Error: "Cotización no disponible"

**Síntomas**:
- Precio muestra "No disponible"
- Datos muy antiguos
- Errores 404 o timeouts

**Soluciones**:

1. **Verificar ticker en Yahoo Finance**:
   - Ir a https://finance.yahoo.com
   - Buscar el ticker manualmente
   - Confirmar que existe y está activo

2. **Verificar horario de mercado**:
   ```python
   # Mercados principales
   NYSE/NASDAQ: 9:30 AM - 4:00 PM EST (L-V)
   London: 8:00 AM - 4:30 PM GMT (L-V)
   Tokyo: 9:00 AM - 3:00 PM JST (L-V)
   ```

3. **Aumentar delays en configuración**:
   ```env
   # En .env
   REQUEST_DELAY_MIN=3.0
   REQUEST_DELAY_MAX=5.0
   ```

4. **Verificar conectividad**:
   ```bash
   # Test directo a Yahoo Finance
   curl -s "https://query1.finance.yahoo.com/v8/finance/chart/AAPL" | head
   ```

#### Error: "Too Many Requests (429)"

**Síntomas**:
```
HTTPError: 429 Client Error: Too Many Requests
```

**Soluciones**:

1. **Aumentar delays**:
   ```env
   REQUEST_DELAY_MIN=5.0
   REQUEST_DELAY_MAX=10.0
   ```

2. **Reducir cantidad de activos**:
   - Eliminar tickers no utilizados
   - Actualizar en lotes más pequeños

3. **Implementar retry logic**:
   ```python
   # Agregar a cotacao_service.py
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2))
   ```

#### Error: "Invalid ticker symbol"

**Síntomas**:
- Ticker no reconocido
- Datos inconsistentes

**Soluciones**:

1. **Verificar formato de ticker**:
   ```bash
   # Formatos correctos
   AAPL      # US stocks
   AAPL.L    # London
   AAPL.TO   # Toronto
   ```

2. **Buscar ticker correcto**:
   - Usar buscador de Yahoo Finance
   - Verificar exchanges disponibles

---

### 🔧 Problemas de Aplicación

#### Error: "Module not found"

**Síntomas**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**Soluciones**:

1. **Verificar entorno virtual**:
   ```bash
   # Activar entorno
   source venv/bin/activate
   
   # Verificar packages instalados
   pip list
   ```

2. **Reinstalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar versión de Python**:
   ```bash
   python --version  # Debe ser 3.12+
   ```

#### Error: "Streamlit not responding"

**Síntomas**:
- Página no carga
- Timeouts
- Error 500

**Soluciones**:

1. **Verificar logs de aplicación**:
   ```bash
   docker-compose logs bolsa_app
   ```

2. **Reiniciar aplicación**:
   ```bash
   docker-compose restart bolsa_app
   ```

3. **Verificar recursos**:
   ```bash
   # Uso de memoria y CPU
   docker stats
   ```

4. **Probar en modo debug**:
   ```bash
   # Configurar LOG_LEVEL=DEBUG en .env
   docker-compose up bolsa_app
   ```

#### Error: "Session state corruption"

**Síntomas**:
- Datos inconsistentes entre páginas
- Formularios no funcionan
- Estado perdido

**Soluciones**:

1. **Limpiar caché del navegador**:
   - Ctrl + F5 (hard refresh)
   - Limpiar cookies de localhost

2. **Reiniciar sesión**:
   - Cerrar todas las pestañas
   - Abrir nueva sesión

3. **Verificar configuración Streamlit**:
   ```toml
   # .streamlit/config.toml
   [server]
   enableCORS = false
   enableXsrfProtection = false
   ```

---

### ⚡ Problemas de Rendimiento

#### Aplicación muy lenta

**Síntomas**:
- Páginas tardan en cargar
- Operaciones lentas
- Timeouts frecuentes

**Diagnóstico**:

1. **Verificar recursos del sistema**:
   ```bash
   # Uso de CPU y memoria
   htop
   docker stats
   ```

2. **Verificar logs para errores**:
   ```bash
   docker-compose logs bolsa_app | grep ERROR
   ```

3. **Verificar conectividad de red**:
   ```bash
   ping google.com
   curl -w "@curl-format.txt" -o /dev/null -s "https://finance.yahoo.com"
   ```

**Soluciones**:

1. **Optimizar configuración de cache**:
   ```env
   CACHE_TIMEOUT=1800  # 30 minutos
   ```

2. **Reducir cantidad de activos**:
   - Eliminar activos no utilizados
   - Agrupar actualizaciones

3. **Incrementar recursos Docker**:
   ```yaml
   # docker-compose.yml
   services:
     bolsa_app:
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: 2.0
   ```

#### Base de datos lenta

**Síntomas**:
- Consultas que tardan mucho
- Timeouts de BD

**Soluciones**:

1. **Verificar índices**:
   ```sql
   -- Conectar a PostgreSQL
   docker-compose exec postgres psql -U postgres -d stock_management
   
   -- Verificar índices
   \di
   ```

2. **Optimizar consultas**:
   ```sql
   -- Ver consultas lentas
   SELECT query, mean_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC;
   ```

3. **Incrementar recursos PostgreSQL**:
   ```yaml
   # docker-compose.yml
   postgres:
     environment:
       - POSTGRES_SHARED_BUFFERS=256MB
       - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
   ```

---

### 🔒 Problemas de Permisos

#### Error: "Permission denied"

**Síntomas**:
```
PermissionError: [Errno 13] Permission denied: '/app/logs'
```

**Soluciones**:

1. **Verificar permisos de directorios**:
   ```bash
   # Linux
   sudo chown -R $USER:$USER ./logs
   sudo chmod -R 755 ./logs
   ```

2. **Verificar usuario Docker**:
   ```dockerfile
   # En Dockerfile, agregar:
   USER root
   RUN chmod 755 /app
   ```

3. **Usar volúmenes con permisos específicos**:
   ```yaml
   # docker-compose.yml
   volumes:
     - ./logs:/app/logs:rw
   ```

#### Error: "Access denied to volume"

**Síntomas**:
- No se pueden escribir datos
- Volúmenes no persisten

**Soluciones**:

1. **Recrear volúmenes**:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

2. **Usar volúmenes nombrados**:
   ```yaml
   volumes:
     postgres_data:
       driver: local
   ```

---

### 📊 Herramientas de Debug

#### Script de Diagnóstico

Crear `debug.sh`:
```bash
#!/bin/bash
echo "=== BolsaV1 Diagnostic Tool ==="
echo ""

echo "1. System Info:"
echo "OS: $(uname -a)"
echo "Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
echo "Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo ""

echo "2. Docker Services:"
docker-compose ps 2>/dev/null || echo "Docker Compose not available"
echo ""

echo "3. Recent App Logs:"
docker-compose logs --tail=20 bolsa_app 2>/dev/null || echo "App logs not available"
echo ""

echo "4. Recent DB Logs:"
docker-compose logs --tail=10 postgres 2>/dev/null || echo "DB logs not available"
echo ""

echo "5. Network Test:"
curl -f http://localhost:8501 >/dev/null 2>&1 && echo "✅ App responding" || echo "❌ App not responding"
echo ""

echo "6. Database Test:"
docker-compose exec -T postgres pg_isready -U postgres 2>/dev/null && echo "✅ DB ready" || echo "❌ DB not ready"
```

#### Health Check Manual

```bash
#!/bin/bash
# health_check.sh

echo "🔍 Health Check BolsaV1"
echo "======================="

# Test App
APP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)
if [ "$APP_STATUS" = "200" ]; then
    echo "✅ App: OK ($APP_STATUS)"
else
    echo "❌ App: FAIL ($APP_STATUS)"
fi

# Test DB
DB_STATUS=$(docker-compose exec -T postgres pg_isready -U postgres 2>/dev/null; echo $?)
if [ "$DB_STATUS" = "0" ]; then
    echo "✅ Database: OK"
else
    echo "❌ Database: FAIL"
fi

# Test Yahoo Finance
YF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://query1.finance.yahoo.com/v8/finance/chart/AAPL")
if [ "$YF_STATUS" = "200" ]; then
    echo "✅ Yahoo Finance: OK"
else
    echo "⚠️ Yahoo Finance: Issues ($YF_STATUS)"
fi
```

---

### 📞 Escalamiento de Problemas

#### Información para Reportes

Cuando reportes un problema, incluye:

1. **Información del sistema**:
   ```bash
   uname -a
   docker --version
   docker-compose --version
   ```

2. **Logs completos**:
   ```bash
   docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
   ```

3. **Configuración (sin passwords)**:
   ```bash
   cat docker-compose.yml
   cat .env | sed 's/password=.*/password=***/'
   ```

4. **Pasos para reproducir**:
   - Qué estabas haciendo
   - Qué esperabas que pasara
   - Qué pasó realmente

#### Canales de Soporte

1. **GitHub Issues**: Para bugs confirmados
2. **GitHub Discussions**: Para preguntas generales
3. **Documentation**: Para consultas de uso

---

**🎯 ¡Problemas Resueltos!**

Si no encuentras solución a tu problema específico, crea un issue en GitHub con toda la información de diagnóstico.

*La mayoría de problemas se resuelven con reiniciar servicios y verificar configuración básica.*