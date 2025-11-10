"""
Página de Histórico

Esta página permite visualizar gráficos de precios históricos de los activos
y analizar su performance a lo largo del tiempo.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ..services import AtivoService, CotacaoService


def show_historico_page():
    """Muestra la página de histórico de precios"""
    st.header("📈 Histórico de Precios")
    
    ativos = AtivoService.listar_ativos()
    if not ativos:
        st.warning("No hay valores registrados. Ve a la sección 'Valores' para añadir algunos.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker_selecionado = st.selectbox(
            "Selecciona un Valor",
            options=[f"{a.ticker} - {a.nome}" for a in ativos]
        )
    
    with col2:
        dias = st.selectbox("Período", [7, 30, 90, 180, 365], index=2)
    
    if ticker_selecionado:
        ticker = ticker_selecionado.split(" - ")[0]
        
        with st.spinner(f"Cargando histórico de {ticker}..."):
            hist = CotacaoService.obter_historico(ticker, dias)
            
            if not hist.empty:
                # Determinar tipo de gráfico
                col1, col2 = st.columns(2)
                with col1:
                    tipo_grafico = st.radio("Tipo de Gráfico", ["Velas", "Línea"], horizontal=True)
                
                with col2:
                    mostrar_volumen = st.checkbox("Mostrar Volumen", value=False)
                
                # Configurar subplot si se muestra volumen
                if mostrar_volumen:
                    from plotly.subplots import make_subplots
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        subplot_titles=(f'{ticker} - Precio', 'Volumen'),
                        row_heights=[0.7, 0.3]
                    )
                else:
                    fig = go.Figure()
                
                # Agregar gráfico de precios
                if tipo_grafico == "Velas":
                    candlestick = go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name=ticker
                    )
                    
                    if mostrar_volumen:
                        fig.add_trace(candlestick, row=1, col=1)
                    else:
                        fig.add_trace(candlestick)
                else:
                    line_trace = go.Scatter(
                        x=hist.index,
                        y=hist['Close'],
                        mode='lines',
                        name=f'{ticker} - Precio de Cierre',
                        line=dict(color='blue', width=2)
                    )
                    
                    if mostrar_volumen:
                        fig.add_trace(line_trace, row=1, col=1)
                    else:
                        fig.add_trace(line_trace)
                
                # Agregar gráfico de volumen si está seleccionado
                if mostrar_volumen:
                    volume_trace = go.Bar(
                        x=hist.index,
                        y=hist['Volume'],
                        name='Volumen',
                        marker=dict(color='lightblue'),
                        opacity=0.7
                    )
                    fig.add_trace(volume_trace, row=2, col=1)
                
                # Configurar layout
                title = f"Histórico de {ticker} - Últimos {dias} días"
                if mostrar_volumen:
                    fig.update_layout(
                        title=title,
                        height=600,
                        xaxis_rangeslider_visible=False
                    )
                    fig.update_yaxes(title_text="Precio (USD)", row=1, col=1)
                    fig.update_yaxes(title_text="Volumen", row=2, col=1)
                    fig.update_xaxes(title_text="Fecha", row=2, col=1)
                else:
                    fig.update_layout(
                        title=title,
                        yaxis_title="Precio (USD)",
                        xaxis_title="Fecha",
                        height=500
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Estadísticas del período
                st.subheader("📊 Estadísticas del Período")
                
                # Calcular métricas adicionales
                precio_inicial = hist['Close'].iloc[0]
                precio_final = hist['Close'].iloc[-1]
                variacion_periodo = precio_final - precio_inicial
                variacion_pct = (variacion_periodo / precio_inicial) * 100
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                col1.metric(
                    "Precio Inicial", 
                    f"${precio_inicial:.2f}"
                )
                col2.metric(
                    "Precio Final", 
                    f"${precio_final:.2f}",
                    delta=f"${variacion_periodo:.2f}"
                )
                col3.metric(
                    "Variación %", 
                    f"{variacion_pct:.2f}%"
                )
                col4.metric(
                    "Rango (Min-Max)", 
                    f"${hist['Low'].min():.2f} - ${hist['High'].max():.2f}"
                )
                col5.metric(
                    "Precio Promedio", 
                    f"${hist['Close'].mean():.2f}"
                )
                
                # Métricas adicionales en una segunda fila
                col1, col2, col3, col4 = st.columns(4)
                
                # Calcular volatilidad (desviación estándar de los retornos diarios)
                returns = hist['Close'].pct_change().dropna()
                volatilidad = returns.std() * (252 ** 0.5) * 100  # Anualizada
                
                col1.metric("Volatilidad Anual", f"{volatilidad:.2f}%")
                col2.metric("Volumen Promedio", f"{int(hist['Volume'].mean()):,}")
                col3.metric("Días con Ganancia", f"{(returns > 0).sum()}")
                col4.metric("Días con Pérdida", f"{(returns < 0).sum()}")
                
                # Análisis técnico básico
                st.markdown("---")
                st.subheader("🔍 Análisis Técnico")
                
                # Calcular medias móviles
                hist['MA20'] = hist['Close'].rolling(window=20).mean()
                hist['MA50'] = hist['Close'].rolling(window=50).mean() if len(hist) >= 50 else None
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if len(hist) >= 20:
                        precio_actual = hist['Close'].iloc[-1]
                        ma20_actual = hist['MA20'].iloc[-1]
                        
                        if precio_actual > ma20_actual:
                            st.success(f"📈 Precio sobre MA20: ${ma20_actual:.2f}")
                        else:
                            st.error(f"📉 Precio bajo MA20: ${ma20_actual:.2f}")
                    else:
                        st.info("📊 Insuficientes datos para MA20")
                
                with col2:
                    if len(hist) >= 50 and hist['MA50'].iloc[-1] is not None:
                        precio_actual = hist['Close'].iloc[-1]
                        ma50_actual = hist['MA50'].iloc[-1]
                        
                        if precio_actual > ma50_actual:
                            st.success(f"📈 Precio sobre MA50: ${ma50_actual:.2f}")
                        else:
                            st.error(f"📉 Precio bajo MA50: ${ma50_actual:.2f}")
                    else:
                        st.info("📊 Insuficientes datos para MA50")
                
                # Tabla de datos recientes
                st.markdown("---")
                st.subheader("📋 Datos Recientes")
                
                # Preparar datos para mostrar
                hist_display = hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                hist_display.columns = ['Apertura', 'Máximo', 'Mínimo', 'Cierre', 'Volumen']
                
                # Formatear números
                for col in ['Apertura', 'Máximo', 'Mínimo', 'Cierre']:
                    hist_display[col] = hist_display[col].apply(lambda x: f"${x:.2f}")
                hist_display['Volumen'] = hist_display['Volumen'].apply(lambda x: f"{int(x):,}")
                
                # Agregar variación diaria
                returns_pct = hist['Close'].pct_change() * 100
                hist_display['Variación %'] = returns_pct.apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                
                st.dataframe(
                    hist_display.sort_index(ascending=False).head(20), 
                    use_container_width=True
                )
                
                # Opción de descarga
                if st.button("📥 Descargar Datos Históricos"):
                    csv = hist.to_csv()
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f"{ticker}_historico_{dias}d.csv",
                        mime="text/csv"
                    )
            
            else:
                st.error(f"❌ No se pudo obtener el histórico de {ticker}. Verifique la conexión a internet.")
                
                # Sugerir alternativas
                st.info("""
                💡 **Sugerencias:**
                - Verifica que el ticker sea correcto
                - Comprueba tu conexión a internet
                - Intenta con un período más corto
                - Algunos tickers pueden no tener datos históricos completos
                """)
    
    # Información adicional
    st.markdown("---")
    st.info("""
    💡 **Información sobre el histórico:**
    - Los datos provienen de Yahoo Finance
    - Los gráficos de velas muestran apertura, máximo, mínimo y cierre
    - La volatilidad se calcula como la desviación estándar anualizada
    - MA20/MA50: Medias móviles de 20 y 50 días respectivamente
    - Puedes cambiar entre vista de velas y líneas
    """)
    
    # Consejos de trading (solo educativos)
    with st.expander("📚 Conceptos de Análisis Técnico"):
        st.markdown("""
        **🕯️ Gráfico de Velas (Candlesticks):**
        - Verde: Precio de cierre > precio de apertura (día positivo)
        - Roja: Precio de cierre < precio de apertura (día negativo)
        - Sombras: Máximo y mínimo del día
        
        **📊 Medias Móviles:**
        - MA20: Tendencia a corto plazo
        - MA50: Tendencia a medio plazo
        - Precio sobre MA: Posible tendencia alcista
        - Precio bajo MA: Posible tendencia bajista
        
        **📈 Volatilidad:**
        - Alta: Mayor riesgo y oportunidad
        - Baja: Menor fluctuación de precios
        
        ⚠️ **Disclaimer**: Esta información es solo educativa. No constituye asesoramiento financiero.
        """)