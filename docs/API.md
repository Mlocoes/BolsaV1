# 🔧 API y Servicios - BolsaV1

## Documentación de Servicios

Esta documentación describe la API interna de servicios de BolsaV1 v2.0.0.

---

## 📦 AtivoService

Servicio principal para gestión de activos financieros.

### Métodos Principales

#### `adicionar_ativo(ticker: str, nome: str = None) -> bool`
Añade un nuevo activo a la base de datos.

**Parámetros:**
- `ticker`: Símbolo del ticker (ej: "AAPL")
- `nome`: Nombre opcional del activo

**Retorna:**
- `bool`: True si se agregó correctamente, False en caso contrario

**Ejemplo:**
```python
from app.services import AtivoService

# Agregar Apple
success = AtivoService.adicionar_ativo("AAPL", "Apple Inc.")
if success:
    print("✅ Activo agregado correctamente")
```

#### `listar_ativos(apenas_ativos: bool = True) -> List[Ativo]`
Lista todos los activos registrados.

**Parámetros:**
- `apenas_ativos`: Si True, solo lista activos activos

**Retorna:**
- `List[Ativo]`: Lista de objetos Ativo

**Ejemplo:**
```python
# Listar solo activos activos
ativos_activos = AtivoService.listar_ativos(apenas_ativos=True)

# Listar todos (incluyendo desactivados)
todos_ativos = AtivoService.listar_ativos(apenas_ativos=False)
```

#### `eliminar_ativo(ticker: str) -> bool`
Elimina un activo y todos sus datos relacionados.

**⚠️ PELIGRO**: Esta operación es irreversible y elimina:
- El activo
- Todas las operaciones
- Todos los precios históricos
- Las posiciones

**Ejemplo:**
```python
# Verificar que no tenga posiciones antes de eliminar
if AtivoService.eliminar_ativo("AAPL"):
    print("✅ Activo eliminado")
```

#### `desactivar_ativo(ticker: str) -> bool`
Desactiva un activo sin eliminar datos.

**Ejemplo:**
```python
# Desactivar temporalmente
AtivoService.desactivar_ativo("AAPL")
```

#### `reactivar_ativo(ticker: str) -> bool`
Reactiva un activo previamente desactivado.

**Ejemplo:**
```python
# Reactivar activo
AtivoService.reactivar_ativo("AAPL")
```

---

## 💹 CotacaoService

Servicio para obtener cotizaciones con sistema de cache inteligente.

### Métodos Principales

#### `obter_cotacao_atual(ticker: str) -> Optional[dict]`
Obtiene la cotización actual con fallbacks automáticos.

**Flujo de Fallback:**
1. Cache local (si no expiró)
2. Yahoo Finance API
3. Base de datos (última cotización guardada)
4. Valores por defecto

**Retorna:**
```python
{
    'ticker': 'AAPL',
    'preco_atual': 150.25,
    'abertura': 149.80,
    'fechamento_anterior': 148.95,
    'variacao_dia': 1.30,
    'variacao_pct': 0.87,
    'volume': 25847391,
    'data': '2024-11-10',
    'fonte': 'YAHOO_FINANCE'  # o 'CACHE_LOCAL', 'BD_FALLBACK', 'VALOR_PADRAO'
}
```

**Ejemplo:**
```python
from app.services import CotacaoService

cotacao = CotacaoService.obter_cotacao_atual("AAPL")
if cotacao:
    print(f"AAPL: ${cotacao['preco_atual']:.2f}")
    print(f"Fuente: {cotacao['fonte']}")
```

#### `obter_historico(ticker: str, dias: int = 30) -> pd.DataFrame`
Obtiene histórico de precios de Yahoo Finance.

**Ejemplo:**
```python
import pandas as pd

# Últimos 30 días
hist = CotacaoService.obter_historico("AAPL", dias=30)
if not hist.empty:
    print(f"Precio mínimo: ${hist['Low'].min():.2f}")
    print(f"Precio máximo: ${hist['High'].max():.2f}")
```

#### `salvar_preco_diario(ativo_id: int, ticker: str) -> bool`
Guarda el precio actual en la base de datos.

**Ejemplo:**
```python
# Guardar precio diario para análisis histórico
success = CotacaoService.salvar_preco_diario(1, "AAPL")
```

### Sistema de Cache

El servicio implementa un cache inteligente:

```python
# Configuración por defecto
CACHE_TIMEOUT = 300  # 5 minutos
cache_key = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}"
```

**Limpieza Automática:**
- Se ejecuta antes de cada consulta
- Elimina entradas expiradas automáticamente

---

## 💼 OperacaoService

Servicio para registro y gestión de operaciones de trading.

### Métodos Principales

#### `registrar_operacao(ativo_id: int, data: datetime, tipo: str, quantidade: int, preco: float) -> bool`
Registra una operación de compra o venta.

**Validaciones Automáticas:**
- Para ventas: Verifica saldo suficiente
- Actualiza posiciones automáticamente
- Rollback en caso de error

**Parámetros:**
- `ativo_id`: ID del activo
- `data`: Fecha de la operación  
- `tipo`: "compra" o "venda"
- `quantidade`: Número de acciones
- `preco`: Precio por acción

**Ejemplo:**
```python
from app.services import OperacaoService
from datetime import datetime

# Registrar compra de 100 acciones de Apple a $150.50
success = OperacaoService.registrar_operacao(
    ativo_id=1,
    data=datetime.now(),
    tipo="compra", 
    quantidade=100,
    preco=150.50
)

if success:
    print("✅ Operación registrada")
    # Se actualiza automáticamente la posición
```

#### `listar_operacoes(ativo_id: Optional[int] = None) -> List[Operacao]`
Lista operaciones con filtro opcional.

**Ejemplo:**
```python
# Todas las operaciones
todas = OperacaoService.listar_operacoes()

# Solo operaciones de un activo específico
aapl_ops = OperacaoService.listar_operacoes(ativo_id=1)
```

#### `obter_resumo_operacoes(ativo_id: int) -> dict`
Obtiene estadísticas resumidas de operaciones.

**Retorna:**
```python
{
    'total_compras': 150,
    'total_vendas': 50, 
    'quantidade_atual': 100,
    'valor_total_compras': 15000.00,
    'valor_total_vendas': 8000.00,
    'preco_medio_compra': 100.00,
    'preco_medio_venda': 160.00,
    'total_operacoes': 5
}
```

---

## 📊 PosicaoService

Servicio para cálculo y gestión de posiciones consolidadas.

### Métodos Principales

#### `atualizar_posicao(ativo_id: int) -> bool`
Recalcula la posición de un activo basada en operaciones.

**Cálculos Automáticos:**
- Cantidad total (compras - ventas)
- Precio medio ponderado
- Resultado acumulado vs precio actual
- Resultado del día vs precio anterior

**Ejemplo:**
```python
from app.services import PosicaoService

# Actualizar posición después de operaciones
PosicaoService.atualizar_posicao(ativo_id=1)
```

#### `obter_resumo_portfolio() -> dict`
Obtiene resumen completo del portfolio.

**Retorna:**
```python
{
    'total_ativos': 5,
    'valor_total_investido': 50000.00,
    'valor_atual_portfolio': 55000.00,
    'resultado_total_dia': 250.00,
    'resultado_total_acumulado': 5000.00,
    'percentual_resultado': 10.0
}
```

#### `atualizar_todas_posicoes() -> bool`
Actualiza todas las posiciones con precios actuales.

**Ejemplo:**
```python
# Actualización masiva (útil al inicio del día)
if PosicaoService.atualizar_todas_posicoes():
    print("✅ Todas las posiciones actualizadas")
```

---

## 🔍 ValidacaoService

Servicio para validación de tickers con múltiples fuentes.

### Función Principal

#### `validar_ticker(ticker: str) -> dict`
Valida un ticker con sistema de fallbacks.

**Proceso de Validación:**
1. Lista de tickers conocidos (offline)
2. Validación online con Yahoo Finance
3. Fallback manual para tickers válidos

**Retorna:**
```python
{
    'valido': True,
    'nome': 'Apple Inc.',
    'ticker': 'AAPL',
    'fonte': 'LISTA_CONOCIDA',  # o 'YAHOO_FINANCE', 'MANUAL', etc.
    'warning': None  # o mensaje de advertencia
}
```

**Ejemplo:**
```python
from app.services import validar_ticker

result = validar_ticker("AAPL")
if result['valido']:
    print(f"✅ {result['ticker']}: {result['nome']}")
    print(f"Fuente: {result['fonte']}")
else:
    print(f"❌ Error: {result['erro']}")
```

---

## 🛠️ Utilidades y Helpers

### Config
Configuración centralizada del sistema.

```python
from app.utils import Config

# Configuración de base de datos
db_config = Config.get_db_config()

# Configuración de cache
cache_config = Config.get_cache_config()

# Configuración de Yahoo Finance
yahoo_config = Config.get_yahoo_config()
```

### Helpers de Formateo

```python
from app.utils import (
    format_currency,
    format_percentage,
    format_number,
    get_icon_for_trend
)

# Formatear valores
price = format_currency(150.25)  # "$150.25"
pct = format_percentage(5.67)    # "5.67%"
vol = format_number(1500000)     # "1,500,000"

# Íconos para tendencias
icon = get_icon_for_trend(2.5)   # "📈"
```

### Logging

```python
from app.utils import get_logger

# Logger específico para módulo
logger = get_logger('mi_modulo')
logger.info("Información importante")
logger.error("Error crítico")
```

---

## 🔗 Integración con Streamlit

### Ejemplo de Página Personalizada

```python
import streamlit as st
from app.services import AtivoService, CotacaoService

def my_custom_page():
    st.header("Mi Página Personalizada")
    
    # Obtener datos
    ativos = AtivoService.listar_ativos()
    
    # Mostrar cotizaciones
    for ativo in ativos:
        cotacao = CotacaoService.obter_cotacao_atual(ativo.ticker)
        if cotacao:
            col1, col2, col3 = st.columns(3)
            col1.metric("Ticker", ativo.ticker)
            col2.metric("Precio", f"${cotacao['preco_atual']:.2f}")
            col3.metric("Variación", f"{cotacao['variacao_pct']:.2f}%")
```

---

## 📋 Códigos de Error Comunes

### AtivoService
- `False + st.warning`: Ticker ya existe
- `False + st.error`: Ticker inválido o error de conexión
- `False + st.error`: Activo tiene posiciones activas (no se puede eliminar)

### CotacaoService
- `None`: No se pudo obtener cotización (verificar logs)
- `fonte: 'BD_FALLBACK'`: API limitada, usando datos de BD
- `fonte: 'VALOR_PADRAO'`: Sin conexión, usando valores por defecto

### OperacaoService
- `False + st.error`: Saldo insuficiente para venta
- `False + st.error`: Error de validación o BD

### PosicaoService
- `False`: Error en cálculo de posición (verificar logs)

---

## 🧪 Testing

### Ejemplos de Testing

```python
# Test básico de servicios
def test_ativo_service():
    # Agregar activo
    success = AtivoService.adicionar_ativo("TEST", "Test Stock")
    assert success
    
    # Listar activos
    ativos = AtivoService.listar_ativos()
    assert any(a.ticker == "TEST" for a in ativos)
    
    # Limpiar
    AtivoService.eliminar_ativo("TEST")

def test_cotacao_service():
    # Test con ticker conocido
    cotacao = CotacaoService.obter_cotacao_atual("AAPL")
    assert cotacao is not None
    assert 'preco_atual' in cotacao
    assert cotacao['ticker'] == 'AAPL'
```

---

## 🔐 Consideraciones de Seguridad

### Validaciones Implementadas
- **SQL Injection**: Uso de SQLAlchemy ORM
- **Input Validation**: Validación de tickers y tipos
- **Error Handling**: Manejo graceful de errores
- **Rate Limiting**: Control de requests a APIs externas

### Buenas Prácticas
- Usar siempre los servicios, nunca acceso directo a modelos
- Manejar excepciones en el código cliente
- Verificar valores de retorno antes de usar
- Usar logging para debugging

---

## 🚀 Performance Tips

### Optimizaciones
- El cache de cotizaciones reduce llamadas a API
- Las posiciones se calculan solo cuando es necesario  
- Los precios históricos se guardan para análisis offline
- Queries optimizadas con índices en BD

### Recomendaciones
- Actualizar posiciones en batch al inicio del día
- Usar cache para cotizaciones frecuentes
- Limitar históricos a períodos razonables
- Monitorear logs para identificar problemas

---

**📚 Esta documentación se mantiene actualizada con cada release de BolsaV1.**