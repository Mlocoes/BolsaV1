# 📊 Sistema de Gestión de Valores Cotizados

Sistema completo de gestión de portafolio de inversiones en bolsa, desarrollado en Python con PostgreSQL. Permite seguimiento en tiempo real de valores, registro de operaciones y análisis de rentabilidad.

## 🎯 Características Principales

- ✅ **Gestión de Valores**: Añadir y seguir tickets de bolsa (AAPL, MSFT, GOOGL, etc.)
- 📈 **Cotizaciones en Tiempo Real**: Obtención automática desde Yahoo Finance
- 💼 **Registro de Operaciones**: Compras y ventas con histórico completo
- 📊 **Posiciones Consolidadas**: Cálculo automático de rentabilidad y resultados
- 📉 **Análisis Histórico**: Gráficos interactivos y estadísticas
- 💾 **Base de Datos Profesional**: PostgreSQL con modelo relacional optimizado

## 🏗️ Arquitectura del Sistema

```
📦 Sistema de Gestión de Valores
├── 📊 Frontend (Streamlit)
│   ├── Interfaz web responsive
│   ├── Gráficos interactivos (Plotly)
│   └── Actualización en tiempo real
│
├── 🔧 Backend (Python)
│   ├── Servicios de negocio
│   ├── Gestión de operaciones
│   └── Cálculos financieros
│
├── 💾 Base de Datos (PostgreSQL)
│   ├── Modelo relacional
│   ├── Vistas optimizadas
│   └── Triggers automáticos
│
└── 🌐 APIs Externas
    └── Yahoo Finance (yfinance)
```

## 🗃️ Modelo de Base de Datos

```
┌────────────────────┐
│      ativos        │ ← Valores/Acciones
├────────────────────┤
│ id SERIAL PK       │
│ ticker VARCHAR(10) │
│ nome VARCHAR(100)  │
│ ativo BOOLEAN      │
└────────────────────┘
         │ 1
         │
         │ N
┌────────────────────┐
│  precos_diarios    │ ← Precios Históricos
├────────────────────┤
│ id SERIAL PK       │
│ ativo_id INT FK    │
│ data DATE          │
│ preco_fechamento   │
└────────────────────┘

┌────────────────────┐
│    operacoes       │ ← Compras/Ventas
├────────────────────┤
│ id SERIAL PK       │
│ ativo_id INT FK    │
│ data DATE          │
│ tipo VARCHAR(10)   │
│ quantidade INT     │
│ preco NUMERIC      │
└────────────────────┘

┌────────────────────┐
│     posicoes       │ ← Posiciones Consolidadas
├────────────────────┤
│ id SERIAL PK       │
│ ativo_id INT FK    │
│ quantidade_total   │
│ preco_medio        │
│ preco_atual        │
│ resultado_dia      │
│ resultado_acum.    │
└────────────────────┘
```

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.11 o superior
- PostgreSQL 13 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/stock-management.git
cd stock-management
```

### Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar PostgreSQL

```bash
# Crear base de datos
createdb stock_management

# Ejecutar script de inicialización
psql -U postgres -d stock_management -f init_database.sql
```

### Paso 5: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

Configuración mínima en `.env`:
```
DATABASE_URL=postgresql://tu_usuario:tu_contraseña@localhost:5432/stock_management
```

### Paso 6: Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

## 📖 Guía de Uso

### 1. Añadir Valores

1. Ve a la sección **"Valores"**
2. Ingresa el ticker (ej: AAPL, MSFT, GOOGL)
3. Opcionalmente añade un nombre descriptivo
4. Haz clic en "Añadir Valor"

### 2. Consultar Cotizaciones

1. Ve a la sección **"Cotizaciones"**
2. Haz clic en "Actualizar Cotizaciones"
3. Visualiza precios actuales, variaciones y volumen

### 3. Registrar Operaciones

1. Ve a la sección **"Operaciones"**
2. Selecciona el valor
3. Elige fecha, tipo (compra/venta), cantidad y precio
4. Haz clic en "Registrar Operación"

### 4. Ver Posiciones

1. Ve a la sección **"Posiciones"**
2. Consulta tu portafolio consolidado
3. Visualiza resultados diarios y acumulados
4. Analiza la rentabilidad de cada posición

### 5. Analizar Histórico

1. Ve a la sección **"Histórico"**
2. Selecciona un valor
3. Elige el período (7, 30, 90, 180 o 365 días)
4. Visualiza gráficos de velas y estadísticas

## 🔧 Funcionalidades Técnicas

### Cálculo de Posiciones

El sistema calcula automáticamente:

- **Cantidad Total**: Suma de compras - suma de ventas
- **Precio Medio**: (Total invertido) / (Cantidad total)
- **Resultado Acumulado**: (Precio actual - Precio medio) × Cantidad
- **Resultado del Día**: (Precio actual - Precio cierre anterior) × Cantidad
- **Rentabilidad %**: (Resultado acumulado / Total invertido) × 100

### Actualización Automática

- Los precios de cierre se guardan automáticamente
- Las posiciones se recalculan después de cada operación
- Timestamps automáticos en todas las tablas

### Validaciones

- Verificación de tickers válidos en Yahoo Finance
- Prevención de duplicados
- Validación de cantidades y precios positivos
- Restricción de tipos de operación (compra/venta)

## 📊 Ejemplos de Uso

### Ejemplo 1: Operación Simple

```
1. Añadir valor: AAPL (Apple Inc.)
2. Registrar compra: 10 acciones a $185.50
3. Consultar posición: 
   - Cantidad: 10
   - Precio medio: $185.50
   - Invertido: $1,855.00
```

### Ejemplo 2: Múltiples Operaciones

```
1. Compra inicial: 10 MSFT a $380.00 = $3,800
2. Compra adicional: 5 MSFT a $390.00 = $1,950
3. Posición resultante:
   - Cantidad total: 15
   - Precio medio: $383.33
   - Total invertido: $5,750
```

### Ejemplo 3: Compra y Venta

```
1. Compra: 20 TSLA a $195.30 = $3,906
2. Venta: 5 TSLA a $205.50 = $1,027.50
3. Posición resultante:
   - Cantidad: 15
   - Precio medio: $195.30
   - Resultado parcial: +$51 (en la venta)
```

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.11+ | Lenguaje principal |
| Streamlit | 1.31.0 | Framework de UI |
| PostgreSQL | 13+ | Base de datos |
| SQLAlchemy | 2.0.25 | ORM |
| yfinance | 0.2.35 | API financiera |
| Plotly | 5.18.0 | Gráficos interactivos |
| Pandas | 2.2.0 | Procesamiento de datos |

## 📁 Estructura del Proyecto

```
stock-management/
│
├── app.py                  # Aplicación principal
├── init_database.sql       # Script SQL de inicialización
├── requirements.txt        # Dependencias Python
├── .env.example           # Configuración de ejemplo
├── README.md              # Este archivo
│
├── logs/                  # Archivos de log (se crea automáticamente)
├── backups/               # Backups de base de datos
│
└── venv/                  # Entorno virtual (no incluido en git)
```

## 🔐 Seguridad

- Las contraseñas se almacenan en variables de entorno
- El archivo `.env` está excluido del control de versiones
- Validación de entrada en todas las operaciones
- Transacciones atómicas en base de datos

## 🐛 Solución de Problemas

### Error: "No se pudo conectar a la base de datos"

**Solución:**
```bash
# Verificar que PostgreSQL está corriendo
sudo service postgresql status

# Verificar credenciales en .env
cat .env
```

### Error: "Ticker no encontrado"

**Causa:** El ticker no existe en Yahoo Finance o está mal escrito

**Solución:** Verificar el ticker correcto en [finance.yahoo.com](https://finance.yahoo.com)

### Error: "Módulo no encontrado"

**Solución:**
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Roadmap

- [ ] Autenticación de usuarios
- [ ] Notificaciones por email
- [ ] Análisis técnico avanzado
- [ ] Exportación a Excel/PDF
- [ ] Alertas de precio
- [ ] Integración con más APIs
- [ ] App móvil
- [ ] Modo multi-portafolio

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👤 Autor

Desarrollado con ❤️ para la gestión profesional de portafolios de inversión.

## 📞 Soporte

- 📧 Email: support@stockmanagement.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/stock-management/issues)
- 📖 Documentación: [Wiki del Proyecto](https://github.com/tu-usuario/stock-management/wiki)

## 🙏 Agradecimientos

- Yahoo Finance por proporcionar datos financieros gratuitos
- La comunidad de Streamlit por el excelente framework
- Todos los contribuidores del proyecto

---

⭐ Si este proyecto te fue útil, no olvides darle una estrella en GitHub!# BolsaV1
