# 📖 Manual de Usuario - BolsaV1

Bienvenido a BolsaV1, tu sistema completo de gestión de cartera de inversiones. Esta guía te enseñará cómo usar todas las funcionalidades paso a paso.

---

## 🚀 Primeros Pasos

### Accediendo al Sistema

1. **Abrir navegador** y navegar a: `http://localhost:8501`
2. **Verificar conexión**: Deberías ver la página principal de BolsaV1
3. **Navegación**: Usar el menú lateral izquierdo para acceder a diferentes secciones

### Interfaz Principal

La aplicación está organizada en 5 secciones principales:

- **📊 Dashboard**: Resumen general de tu cartera
- **💎 Gestión de Valores**: Agregar y gestionar activos financieros
- **📈 Cotizaciones**: Monitorear precios en tiempo real
- **💼 Registro de Operaciones**: Registrar compras y ventas
- **🎯 Posiciones**: Ver consolidado de tu cartera
- **📉 Análisis Histórico**: Gráficos y análisis técnico

---

## 📊 Dashboard - Vista General

### Qué Verás

El dashboard te muestra un resumen completo de tu cartera:

- **Total de Activos**: Cantidad de valores diferentes en tu cartera
- **Total Operaciones**: Número total de transacciones realizadas
- **Valor Total de Cartera**: Valor actual de todas tus posiciones
- **Rendimiento**: Ganancia o pérdida total

### Interpretando los Datos

- **🟢 Verde**: Ganancias positivas
- **🔴 Rojo**: Pérdidas
- **📊 Gráficos**: Distribución de tu cartera por activo

### Alertas Importantes

El dashboard te alertará sobre:
- Activos sin cotizaciones recientes
- Posiciones con pérdidas significativas
- Recomendaciones de diversificación

---

## 💎 Gestión de Valores

### Agregando tu Primer Activo

1. **Ir a "Gestión de Valores"** en el menú lateral
2. **Completar el formulario**:
   - **Ticker**: Símbolo del activo (ej: AAPL, GOOGL, MSFT)
   - **Nombre**: Nombre descriptivo (se autocompleta)
3. **Hacer clic en "Agregar Valor"**

**💡 Consejo**: Usa tickers reconocidos por Yahoo Finance. Ejemplos comunes:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google/Alphabet)
- AMZN (Amazon)
- TSLA (Tesla)

### Gestionando Activos Existentes

#### Ver Lista de Activos

La tabla muestra:
- **Ticker**: Símbolo del activo
- **Nombre**: Nombre completo
- **Estado**: Activo/Inactivo
- **Acciones**: Botones para gestionar

#### Eliminar un Activo

1. **Hacer clic en "🗑️ Eliminar"** en la fila correspondiente
2. **Confirmar la acción**

**⚠️ Advertencia**: Solo puedes eliminar activos que no tengan operaciones registradas.

#### Estados de Activos

- **✅ Activo**: Funcionando correctamente
- **⚠️ Warning**: Problemas menores (ej: cotización antigua)
- **❌ Error**: Problemas graves (ej: ticker no encontrado)

### Mejores Prácticas

- **Verificar Tickers**: Confirma que el ticker existe antes de agregarlo
- **Nombres Descriptivos**: Usa nombres claros para identificar fácilmente
- **Revisar Regularmente**: Elimina activos que ya no uses

---

## 📈 Cotizaciones - Precios en Tiempo Real

### Vista Principal

La sección de cotizaciones te muestra:
- **Precio Actual**: Último precio disponible
- **Cambio del Día**: Variación absoluta y porcentual
- **Horario de Actualización**: Cuándo se obtuvo la última cotización

### Actualizando Precios

1. **Hacer clic en "🔄 Actualizar Cotizaciones"**
2. **Esperar**: El sistema consulta automáticamente los precios
3. **Verificar Timestamp**: Confirma que los datos son recientes

**⏱️ Nota**: Las actualizaciones pueden tardar varios segundos dependiendo de la cantidad de activos.

### Interpretando las Cotizaciones

#### Colores en las Cotizaciones

- **🟢 Verde**: Precio subió respecto al cierre anterior
- **🔴 Rojo**: Precio bajó respecto al cierre anterior
- **⚪ Neutral**: Sin cambio o datos insuficientes

#### Información Mostrada

- **Precio**: Valor actual de la acción
- **Cambio ($)**: Diferencia en valor absoluto
- **Cambio (%)**: Diferencia en porcentaje
- **Actualizado**: Timestamp de la última actualización

### Problemas Comunes

#### Cotización No Disponible

**Síntomas**: Aparece "No disponible" o datos muy antiguos

**Soluciones**:
1. Verificar que el ticker sea correcto
2. Comprobar que el mercado esté abierto
3. Intentar actualizar manualmente

#### Datos Desactualizados

**Síntomas**: Timestamp muy antiguo

**Causas Comunes**:
- Mercado cerrado
- Problemas temporales de API
- Ticker suspendido o descontinuado

---

## 💼 Registro de Operaciones

### Tipos de Operación

- **Compra**: Adquisición de acciones
- **Venta**: Venta de acciones
- **Dividendo**: Pago de dividendos (próximamente)

### Registrando una Compra

1. **Seleccionar "Compra"** como tipo de operación
2. **Completar formulario**:
   - **Activo**: Seleccionar de la lista desplegable
   - **Cantidad**: Número de acciones compradas
   - **Precio**: Precio por acción al momento de compra
   - **Fecha**: Fecha de la operación (por defecto: hoy)
3. **Hacer clic en "Registrar Operación"**

**📝 Ejemplo de Compra**:
- Activo: AAPL
- Cantidad: 10
- Precio: 150.00
- Fecha: 2024-01-15
- Total: $1,500.00

### Registrando una Venta

1. **Seleccionar "Venta"** como tipo de operación
2. **Completar formulario** similar a la compra
3. **Verificar posición disponible**: No puedes vender más de lo que tienes

**📝 Ejemplo de Venta**:
- Activo: AAPL
- Cantidad: 5 (de las 10 que tenías)
- Precio: 180.00
- Fecha: 2024-03-15
- Total: $900.00
- Ganancia: $150.00 (($180-$150) × 5)

### Histórico de Operaciones

#### Vista de Tabla

El histórico muestra:
- **Fecha**: Cuándo se realizó la operación
- **Tipo**: Compra/Venta
- **Activo**: Ticker del activo
- **Cantidad**: Número de acciones
- **Precio**: Precio por acción
- **Total**: Valor total de la operación

#### Filtros y Búsqueda

- **Por Fecha**: Filtra operaciones por rango de fechas
- **Por Activo**: Muestra solo operaciones de un activo específico
- **Por Tipo**: Compras o ventas únicamente

### Validaciones del Sistema

El sistema previene errores comunes:

- **Venta sin Stock**: No puedes vender más acciones de las que posees
- **Precios Negativos**: No se permiten precios o cantidades negativas
- **Fechas Futuras**: No se permiten operaciones en fechas futuras
- **Activos Inexistentes**: Solo puedes operar con activos previamente agregados

---

## 🎯 Posiciones - Tu Cartera Consolidada

### Vista General de Posiciones

Esta sección te muestra el estado actual de todas tus inversiones:

#### Información por Activo

- **Ticker**: Símbolo del activo
- **Cantidad**: Acciones que posees actualmente
- **Precio Promedio**: Precio promedio ponderado de tus compras
- **Precio Actual**: Última cotización disponible
- **Valor Total**: Valor actual de tu posición (Cantidad × Precio Actual)
- **P&L**: Ganancia o pérdida no realizada
- **P&L %**: Porcentaje de ganancia o pérdida

### Entendiendo tus Posiciones

#### Precio Promedio Ponderado

Cuando compras el mismo activo en diferentes momentos y precios, el sistema calcula automáticamente tu precio promedio:

**📊 Ejemplo**:
- Compra 1: 10 acciones AAPL a $100 = $1,000
- Compra 2: 5 acciones AAPL a $120 = $600
- **Total**: 15 acciones por $1,600
- **Precio Promedio**: $1,600 ÷ 15 = $106.67

#### P&L (Ganancia/Pérdida)

- **P&L Absoluto**: Diferencia en dólares entre valor actual y costo
- **P&L Porcentual**: Porcentaje de ganancia o pérdida

**🧮 Cálculo**:
- Costo Total: Cantidad × Precio Promedio
- Valor Actual: Cantidad × Precio Actual
- P&L: Valor Actual - Costo Total
- P&L %: (P&L ÷ Costo Total) × 100

#### Interpretación de Colores

- **🟢 Verde**: Posición en ganancia
- **🔴 Rojo**: Posición en pérdida
- **⚪ Gris**: Posición neutra o sin datos

### Acciones desde Posiciones

#### Vender Posición

1. **Hacer clic en "Vender"** en la fila de la posición
2. **Se abre formulario pre-llenado** con datos actuales
3. **Ajustar cantidad** si no quieres vender todo
4. **Confirmar venta**

#### Análisis Detallado

Para cada posición puedes ver:
- Histórico de todas las operaciones
- Evolución del precio promedio
- Gráfico de performance
- Distribución en tu cartera

### Consolidado de Cartera

#### Métricas Totales

- **Valor Total de Cartera**: Suma de todas las posiciones
- **Inversión Total**: Total invertido (suma de compras - ventas)
- **Ganancia/Pérdida Total**: P&L consolidado
- **Porcentaje de Rendimiento**: Performance general de la cartera

#### Distribución de Activos

Gráfico que muestra:
- **Peso por Activo**: Qué porcentaje representa cada posición
- **Concentración de Riesgo**: Identifica si estás muy concentrado
- **Diversificación**: Nivel de diversificación de tu cartera

---

## 📉 Análisis Histórico

### Gráficos de Precios

#### Vista de Precio Individual

1. **Seleccionar un activo** del dropdown
2. **Elegir período**: 1M, 3M, 6M, 1A, 2A
3. **Tipo de gráfico**: Línea o Candlesticks

#### Indicadores Técnicos

- **Medias Móviles**: 20, 50, 200 días
- **Bandas de Bollinger**: Volatilidad del activo
- **RSI**: Índice de Fuerza Relativa
- **MACD**: Convergencia/Divergencia de medias móviles

### Análisis de Portfolio

#### Performance Histórica

- **Evolución del Valor**: Cómo ha cambiado tu cartera en el tiempo
- **Drawdown**: Máxima pérdida desde el pico más alto
- **Volatilidad**: Medida de riesgo de tu cartera

#### Comparación con Benchmarks

- **S&P 500**: Comparación con el mercado general
- **Sectores**: Performance vs sectores específicos
- **Beta**: Sensibilidad de tu cartera al mercado

### Reportes y Exportación

#### Generar Reportes

1. **Seleccionar período** de análisis
2. **Elegir formato**: PDF, Excel, CSV
3. **Hacer clic en "Generar Reporte"**

#### Contenido de Reportes

- **Resumen Ejecutivo**: Métricas principales
- **Detalle de Posiciones**: Estado actual de cada activo
- **Histórico de Operaciones**: Todas las transacciones
- **Análisis de Performance**: Gráficos y métricas de rendimiento

---

## 🛠️ Tips y Mejores Prácticas

### Para Nuevos Usuarios

1. **Empieza Simple**: Agrega 2-3 activos conocidos
2. **Registra Todo**: Mantén historial completo de operaciones
3. **Revisa Regularmente**: Actualiza cotizaciones frecuentemente
4. **Diversifica**: No concentres todo en un solo activo

### Gestión de Riesgo

#### Diversificación

- **Por Sector**: No todo en tecnología o servicios financieros
- **Por Geografía**: Considera activos de diferentes países
- **Por Tamaño**: Mezcla large-caps con small-caps
- **Por Tipo**: Acciones, ETFs, etc.

#### Seguimiento de Performance

- **Revisa Mensualmente**: Analiza evolución de posiciones
- **Compara con Benchmarks**: ¿Estás superando al S&P 500?
- **Ajusta Estrategia**: Modifica según resultados

### Gestión de Datos

#### Mantenimiento Regular

- **Limpia Activos No Usados**: Elimina tickers que no operas
- **Verifica Cotizaciones**: Asegúrate que los precios sean correctos
- **Backup de Datos**: Exporta reportes regularmente

#### Solución de Problemas

- **Cotizaciones Incorrectas**: Verifica ticker en Yahoo Finance
- **Cálculos Extraños**: Revisa que todas las operaciones estén registradas
- **Performance Lenta**: Reduce cantidad de activos o aumenta intervalos de cache

---

## 🚨 Resolución de Problemas Comunes

### Problemas con Cotizaciones

#### "Cotización no disponible"

**Posibles Causas**:
- Ticker incorrecto o no existe
- Mercado cerrado (fin de semana/feriados)
- Problemas temporales de API

**Soluciones**:
1. Verificar ticker en Yahoo Finance
2. Esperar a horario de mercado
3. Intentar actualización manual más tarde

#### Precios muy antiguos

**Causas**:
- Activo poco líquido
- Ticker descontinuado
- Problemas de conectividad

**Soluciones**:
1. Verificar si el activo sigue cotizando
2. Buscar ticker alternativo
3. Eliminar activo si ya no es relevante

### Problemas con Operaciones

#### No puedo registrar venta

**Error**: "No tienes suficientes acciones"

**Solución**: Verificar que tienes la cantidad que intentas vender en la sección "Posiciones"

#### Cálculos incorrectos

**Síntomas**: P&L no coincide con expectativas

**Verificación**:
1. Revisar todas las operaciones en el histórico
2. Confirmar que no faltan transacciones
3. Verificar fechas y precios registrados

### Problemas de Rendimiento

#### La aplicación está lenta

**Posibles Causas**:
- Muchos activos sin cotizaciones
- Cache lleno
- Conectividad lenta

**Soluciones**:
1. Eliminar activos no utilizados
2. Reiniciar aplicación (refrescar navegador)
3. Verificar conexión a internet

#### Timeouts en cotizaciones

**Síntomas**: "Error al obtener cotizaciones"

**Soluciones**:
1. Reducir cantidad de activos
2. Intentar más tarde
3. Verificar que Yahoo Finance esté accesible

---

## 📞 Soporte y Ayuda

### Información para Soporte

Cuando reportes un problema, incluye:

1. **Pasos para Reproducir**: Qué estabas haciendo cuando ocurrió
2. **Error Exacto**: Mensaje de error completo
3. **Navegador**: Chrome, Firefox, Safari, etc.
4. **Activos Afectados**: Qué tickers tienen problemas
5. **Timestamp**: Cuándo ocurrió el problema

### Logs y Debugging

Para problemas técnicos:
```bash
# Ver logs recientes
docker-compose logs --tail=100 bolsa_app

# Estado de servicios
docker-compose ps
```

### Recursos Adicionales

- **Documentación Técnica**: Ver `/docs/` en el proyecto
- **FAQ**: Preguntas frecuentes en GitHub
- **Issues**: Reportar bugs en GitHub Issues
- **Updates**: Seguir releases para nuevas funcionalidades

---

## 📈 Próximas Funcionalidades

### En Desarrollo

- **Alertas de Precios**: Notificaciones cuando un activo alcance cierto precio
- **Análisis Fundamental**: Ratios financieros y métricas empresariales
- **Portfolio Optimization**: Sugerencias de diversificación automática
- **Mobile App**: Versión para dispositivos móviles

### Funcionalidades Avanzadas Planificadas

- **Paper Trading**: Simulación de operaciones sin dinero real
- **Risk Management**: Herramientas avanzadas de gestión de riesgo
- **Tax Reporting**: Reportes para declaración de impuestos
- **Social Features**: Compartir estrategias con otros usuarios

---

**🎯 ¡Listo para Invertir!**

Con esta guía ya tienes todo lo necesario para sacar el máximo provecho a BolsaV1. ¡Empieza construyendo tu cartera y monitoreando tus inversiones!

*Para preguntas específicas o problemas técnicos, consulta la documentación técnica o crea un issue en GitHub.*