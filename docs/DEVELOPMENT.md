# 💻 Guía de Desarrollo - BolsaV1

## Configuración del Entorno de Desarrollo

Esta guía está dirigida a desarrolladores que quieren contribuir o extender BolsaV1.

---

## 🛠️ Configuración Inicial

### Requisitos del Sistema
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 15 (para desarrollo local)
- Git
- VS Code (recomendado)

### Setup del Proyecto

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd BolsaV1

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno para desarrollo
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/stock_management"
export LOG_LEVEL="DEBUG"
export CACHE_TIMEOUT="60"  # Cache más corto para desarrollo
```

### Configuración de PostgreSQL Local

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib  # Ubuntu
brew install postgresql  # macOS

# Crear base de datos
sudo -u postgres createdb stock_management
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

---

## 🏗️ Arquitectura de Desarrollo

### Principios de Diseño

1. **Separación de Responsabilidades**
   - `models/`: Solo definiciones de esquema de BD
   - `services/`: Lógica de negocio exclusivamente
   - `pages/`: UI y presentación únicamente
   - `utils/`: Utilidades sin estado

2. **Configuración Centralizada**
   - Todo desde `app.utils.Config`
   - Variables de entorno para diferentes ambientes
   - No hardcodear valores en el código

3. **Error Handling Robusto**
   - Logging detallado en todos los niveles
   - Rollback automático en operaciones de BD
   - Fallbacks para servicios externos

4. **Testing Friendly**
   - Servicios sin dependencias circulares
   - Funciones puras donde sea posible
   - Mocks para servicios externos

### Estructura Modular Detallada

```
app/
├── models/              # 📊 SQLAlchemy Models
│   ├── base.py         # Configuración base (engine, session)
│   ├── ativo.py        # Modelo de activos
│   ├── operacao.py     # Modelo de operaciones
│   ├── posicao.py      # Modelo de posiciones
│   └── preco_diario.py # Modelo de precios históricos
│
├── services/           # 🔧 Business Logic Layer
│   ├── ativo_service.py      # CRUD de activos + validaciones
│   ├── cotacao_service.py    # API calls + cache + fallbacks
│   ├── operacao_service.py   # Registro ops + validaciones
│   ├── posicao_service.py    # Cálculos + consolidación
│   └── validacao_service.py  # Validación multi-nivel
│
├── pages/              # 🖥️ Streamlit UI Pages
│   ├── valores.py      # Gestión de activos
│   ├── cotizaciones.py # Dashboard de cotizaciones
│   ├── operaciones.py  # Registro y histórico de ops
│   ├── posiciones.py   # Portfolio consolidado
│   └── historico.py    # Análisis técnico y gráficos
│
└── utils/              # 🛠️ Shared Utilities
    ├── config.py       # Configuración centralizada
    ├── database.py     # Inicialización BD + health checks
    ├── helpers.py      # Formateo + validaciones + stats
    └── logging_config.py # Sistema de logging profesional
```

---

## 🧩 Patrones de Código

### Service Pattern

Todos los servicios siguen el mismo patrón:

```python
class MiService:
    """Documentación del servicio"""
    
    @staticmethod
    def operacion_principal(param: tipo) -> tipo_retorno:
        """
        Descripción de la operación
        
        Args:
            param: Descripción del parámetro
            
        Returns:
            tipo_retorno: Descripción del retorno
            
        Raises:
            TipoError: Cuándo se produce
        """
        session = SessionLocal()
        logger = get_logger(__name__)
        
        try:
            # Lógica principal
            logger.info(f"Iniciando operación: {param}")
            
            # Validaciones
            if not validacion:
                logger.warning("Validación fallida")
                st.warning("Mensaje para usuario")
                return False
            
            # Operación principal
            resultado = hacer_operacion()
            session.commit()
            
            logger.info("Operación exitosa")
            st.success("Operación completada")
            return resultado
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error en operación: {e}", exc_info=True)
            st.error(f"Error: {e}")
            return None
        finally:
            session.close()
```

### Page Pattern

Las páginas siguen una estructura consistente:

```python
def show_mi_pagina():
    """Muestra la página de mi funcionalidad"""
    
    # Header
    st.header("🎯 Mi Funcionalidad")
    
    # Verificar prerequisites
    if not prerequisito:
        st.warning("Prerequisito no cumplido")
        return
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Funcionalidad principal
        with st.form("mi_form"):
            datos = recopilar_datos()
            submitted = st.form_submit_button("Enviar")
            
            if submitted:
                if MiService.procesar(datos):
                    st.rerun()
    
    with col2:
        # Info auxiliar o stats
        mostrar_info_auxiliar()
    
    # Sección de datos
    st.markdown("---")
    st.subheader("Datos")
    mostrar_datos_principales()
    
    # Footer con ayuda
    st.info("💡 Información de ayuda")
```

### Model Pattern

Los modelos son definiciones limpias de SQLAlchemy:

```python
class MiModelo(Base):
    """Documentación del modelo"""
    __tablename__ = "mi_tabla"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    campo_requerido = Column(String(100), nullable=False)
    campo_opcional = Column(Integer, default=0)
    
    # Constraints
    campo_con_check = Column(
        String(10), 
        CheckConstraint("campo_con_check IN ('valor1','valor2')"),
        nullable=False
    )
    
    # Relaciones
    relacion = relationship("OtroModelo", back_populates="mi_modelo")
    
    def __repr__(self):
        return f"<MiModelo(id={self.id}, campo={self.campo_requerido})>"
```

---

## 🔧 Herramientas de Desarrollo

### VS Code Configuración Recomendada

`.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "files.associations": {
        "*.py": "python"
    }
}
```

### Extensiones Recomendadas
- Python
- SQLAlchemy
- Docker
- GitLens
- Better Comments

### Pre-commit Hooks

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

---

## 🧪 Testing y Calidad

### Estructura de Tests

```
tests/
├── test_models.py      # Tests de modelos SQLAlchemy
├── test_services.py    # Tests de lógica de negocio
├── test_pages.py       # Tests de UI (mocked)
├── test_utils.py       # Tests de utilidades
└── conftest.py         # Configuración de pytest
```

### Testing de Servicios

```python
import pytest
from app.services import AtivoService
from app.models import SessionLocal

@pytest.fixture
def db_session():
    """Fixture para sesión de BD de test"""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

def test_adicionar_ativo_success():
    """Test exitoso de agregar activo"""
    resultado = AtivoService.adicionar_ativo("TEST", "Test Stock")
    assert resultado is True
    
    # Verificar que existe
    ativos = AtivoService.listar_ativos()
    assert any(a.ticker == "TEST" for a in ativos)
    
    # Cleanup
    AtivoService.eliminar_ativo("TEST")

def test_adicionar_ativo_duplicado():
    """Test de agregar activo duplicado"""
    # Agregar primero
    AtivoService.adicionar_ativo("TEST", "Test Stock")
    
    # Intentar agregar de nuevo
    resultado = AtivoService.adicionar_ativo("TEST", "Test Stock 2")
    assert resultado is False
    
    # Cleanup
    AtivoService.eliminar_ativo("TEST")
```

### Testing de UI (Mocked)

```python
import streamlit as st
from unittest.mock import patch, MagicMock
from app.pages import show_valores_page

def test_valores_page_no_ativos():
    """Test página valores sin activos"""
    with patch('app.services.AtivoService.listar_ativos') as mock_list:
        mock_list.return_value = []
        
        # Ejecutar página (no debería generar errores)
        show_valores_page()
        
        # Verificar que se llamó el servicio
        mock_list.assert_called_once()
```

### Comando de Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests con coverage
pytest --cov=app tests/

# Tests específicos
pytest tests/test_services.py::test_adicionar_ativo_success -v
```

---

## 📊 Logging y Debugging

### Sistema de Logging

El sistema usa múltiples niveles de logging:

```python
from app.utils import get_logger

logger = get_logger('mi_modulo')

# Niveles disponibles
logger.debug("Información detallada para debugging")
logger.info("Eventos normales de la aplicación")
logger.warning("Situaciones inesperadas pero manejadas")
logger.error("Errores que requieren atención")
logger.critical("Errores críticos del sistema")
```

### Configuración por Ambiente

```bash
# Desarrollo
export LOG_LEVEL="DEBUG"

# Producción  
export LOG_LEVEL="INFO"

# Testing
export LOG_LEVEL="WARNING"
```

### Debugging con Streamlit

```python
import streamlit as st
from app.utils import Config

# Solo en desarrollo
if Config.LOG_LEVEL == "DEBUG":
    st.sidebar.markdown("---")
    st.sidebar.markdown("🔍 **Debug Info**")
    st.sidebar.code(f"Session ID: {st.session_state.get('session_id', 'N/A')}")
    st.sidebar.code(f"Cache size: {len(getattr(CotacaoService, 'cotizacoes_cache', {}))}")
```

---

## 🔄 Workflow de Desarrollo

### Git Flow

```bash
# 1. Crear branch feature
git checkout -b feature/nueva-funcionalidad

# 2. Desarrollar con commits descriptivos
git add .
git commit -m "feat: agregar nueva funcionalidad X"

# 3. Tests antes de push
pytest tests/

# 4. Push y PR
git push origin feature/nueva-funcionalidad
# Crear Pull Request en GitHub
```

### Convenciones de Commits

```
feat: nueva funcionalidad
fix: corrección de bug
docs: actualización de documentación
style: cambios de formato (no afectan funcionalidad)
refactor: reestructuración de código
test: agregar o corregir tests
chore: tareas de mantenimiento
```

### Code Review Checklist

- [ ] Código sigue patrones establecidos
- [ ] Funciones documentadas con docstrings
- [ ] Tests agregados para nueva funcionalidad
- [ ] No hay hardcoded values
- [ ] Error handling implementado
- [ ] Logging apropiado agregado
- [ ] Variables de entorno usadas correctamente

---

## 🚀 Deployment

### Docker para Desarrollo

```bash
# Build para desarrollo (con debugging)
docker-compose -f docker-compose.dev.yml up --build

# Variables para desarrollo
export LOG_LEVEL=DEBUG
export CACHE_TIMEOUT=60
```

### Preparación para Producción

```bash
# Build optimizado
docker-compose build --no-cache

# Testing de imagen
docker run --rm bolsav1_bolsa_app streamlit run main.py --help
```

### Environment Variables

```bash
# Desarrollo
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stock_management
LOG_LEVEL=DEBUG
CACHE_TIMEOUT=60
REQUEST_DELAY_MIN=0.5
REQUEST_DELAY_MAX=1.0

# Producción
DATABASE_URL=postgresql://user:pass@prod_host:5432/stock_management
LOG_LEVEL=INFO
CACHE_TIMEOUT=600
REQUEST_DELAY_MIN=2.0
REQUEST_DELAY_MAX=4.0
```

---

## 📈 Performance y Optimización

### Profiling

```python
import cProfile
import io
import pstats

def profile_function():
    """Profiling de función específica"""
    pr = cProfile.Profile()
    pr.enable()
    
    # Ejecutar código a perfilar
    resultado = mi_funcion_lenta()
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print(s.getvalue())
    return resultado
```

### Monitoring

```python
import time
from app.utils import get_logger

def monitor_performance(func):
    """Decorator para monitorear performance"""
    def wrapper(*args, **kwargs):
        logger = get_logger('performance')
        start = time.time()
        
        result = func(*args, **kwargs)
        
        duration = time.time() - start
        if duration > 1.0:  # Log si toma más de 1 segundo
            logger.warning(f"{func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper

# Uso
@monitor_performance
def operacion_lenta():
    pass
```

### Optimizaciones Implementadas

1. **Cache de Cotizaciones**: Reduce llamadas a Yahoo Finance
2. **Lazy Loading**: Páginas se cargan solo cuando se necesitan
3. **Batch Updates**: Actualizaciones masivas de posiciones
4. **Connection Pooling**: SQLAlchemy maneja pool de conexiones
5. **Query Optimization**: Índices en campos frecuentemente consultados

---

## 🔒 Seguridad

### Validación de Inputs

```python
from app.utils import validate_ticker_format

def validar_entrada_usuario(ticker: str) -> bool:
    """Validar entrada del usuario"""
    # Limpiar input
    ticker = ticker.strip().upper()
    
    # Validar formato
    if not validate_ticker_format(ticker):
        return False
    
    # Validar longitud
    if len(ticker) > 10:
        return False
    
    # Validar caracteres permitidos
    if not ticker.isalpha():
        return False
    
    return True
```

### SQL Injection Prevention

```python
# ✅ CORRECTO - Usar SQLAlchemy ORM
session.query(Ativo).filter(Ativo.ticker == user_input).first()

# ❌ INCORRECTO - SQL crudo con input directo
session.execute(f"SELECT * FROM ativos WHERE ticker = '{user_input}'")

# ✅ CORRECTO - Si necesitas SQL crudo, usar parámetros
session.execute(text("SELECT * FROM ativos WHERE ticker = :ticker"), {"ticker": user_input})
```

### Error Handling Seguro

```python
def operacion_segura():
    """Operación con error handling seguro"""
    try:
        # Operación riesgosa
        resultado = operacion_externa()
        return resultado
        
    except ExternalAPIError as e:
        # Log error sin exponer detalles internos
        logger.error(f"API error: {type(e).__name__}")
        st.error("Error de conexión externa. Intenta más tarde.")
        return None
        
    except Exception as e:
        # Log detallado para debugging (no mostrar al usuario)
        logger.error(f"Unexpected error: {e}", exc_info=True)
        st.error("Error inesperado. El equipo ha sido notificado.")
        return None
```

---

## 📚 Recursos de Referencia

### Documentación Externa
- [Streamlit Docs](https://docs.streamlit.io/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [yfinance Docs](https://github.com/ranaroussi/yfinance)
- [Plotly Python](https://plotly.com/python/)

### Patrones de Código
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Streamlit Best Practices](https://docs.streamlit.io/knowledge-base)

### Herramientas Útiles
- [SQLAlchemy Inspector](https://docs.sqlalchemy.org/en/20/core/reflection.html)
- [Streamlit Debugger](https://docs.streamlit.io/knowledge-base/using-streamlit/how-do-i-run-my-streamlit-script)
- [PostgreSQL Admin](https://www.pgadmin.org/)

---

## 🤝 Contribución

### Issues y Feature Requests

1. **Issues**: Usar template de issue con detalles específicos
2. **Feature Requests**: Explicar use case y beneficios
3. **Bug Reports**: Incluir steps to reproduce y logs relevantes

### Pull Request Guidelines

1. **Descripción Clara**: Qué problema resuelve o qué funcionalidad agrega
2. **Tests**: Agregar tests para nueva funcionalidad
3. **Documentación**: Actualizar docs si es necesario
4. **Backward Compatibility**: No romper APIs existentes
5. **Performance**: Considerar impacto en performance

### Code Standards

- **Formatting**: Black con line length 88
- **Imports**: isort con profile black
- **Docstrings**: Google style
- **Type Hints**: Obligatorio para APIs públicas
- **Error Messages**: En español para coherencia

---

**🎯 ¡Happy Coding!**

*Esta guía se actualiza regularmente. Para preguntas específicas, crear issue en GitHub.*