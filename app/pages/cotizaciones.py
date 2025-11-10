"""
Página de Cotizaciones

Esta página muestra las cotizaciones en tiempo real de los activos registrados
y permite actualizar los precios.
"""

import streamlit as st
import pandas as pd
from ..services import AtivoService, CotacaoService


def show_cotizaciones_page():
    """Muestra la página de cotizaciones en tiempo real"""
    st.header("💹 Cotizaciones en Tiempo Real")
    
    ativos = AtivoService.listar_ativos()
    if not ativos:
        st.warning("No hay valores registrados. Ve a la sección 'Valores' para añadir algunos.")
        return
    
    if st.button("🔄 Actualizar Cotizaciones", type="primary"):
        st.rerun()
    
    st.markdown("---")
    
    data_cotacoes = []
    for ativo in ativos:
        with st.spinner(f"Obteniendo {ativo.ticker}..."):
            cotacao = CotacaoService.obter_cotacao_atual(ativo.ticker)
            if cotacao:
                # Determinar color para la variación
                color = "🟢" if cotacao['variacao_dia'] >= 0 else "🔴"
                
                data_cotacoes.append({
                    'Ticker': cotacao['ticker'],
                    'Precio Actual': f"${cotacao['preco_atual']:.2f}",
                    'Apertura': f"${cotacao['abertura']:.2f}",
                    'Cierre Anterior': f"${cotacao['fechamento_anterior']:.2f}",
                    'Variación': f"{color} ${cotacao['variacao_dia']:.2f}",
                    'Variación %': f"{cotacao['variacao_pct']:.2f}%",
                    'Volumen': f"{cotacao['volume']:,}",
                    'Fuente': cotacao.get('fonte', 'N/A')
                })
                
                # Guardar precio diario
                CotacaoService.salvar_preco_diario(ativo.id, ativo.ticker)
    
    if data_cotacoes:
        df_cotacoes = pd.DataFrame(data_cotacoes)
        st.dataframe(df_cotacoes, use_container_width=True)
        
        # Información sobre fuentes de datos
        fuentes = set([item['Fuente'] for item in data_cotacoes])
        if fuentes:
            st.markdown("---")
            st.markdown("**📊 Fuentes de datos:**")
            
            fuente_info = {
                'YAHOO_FINANCE': '🌐 Yahoo Finance (tiempo real)',
                'CACHE_LOCAL': '⚡ Cache local (actualizado)',
                'BD_FALLBACK': '💾 Base de datos (fallback)',
                'VALOR_PADRAO': '⚠️ Valor por defecto (sin conexión)'
            }
            
            for fuente in fuentes:
                if fuente in fuente_info:
                    st.info(fuente_info[fuente])
    else:
        st.error("No se pudieron obtener cotizaciones para ningún activo")
    
    # Información adicional
    st.markdown("---")
    st.info("""
    💡 **Información sobre las cotizaciones:**
    - Los precios se actualizan en tiempo real desde Yahoo Finance
    - Se incluye sistema de cache para optimizar las consultas
    - En caso de problemas de conexión, se usan datos de la base de datos
    - Los precios diarios se guardan automáticamente para históricos
    """)
    
    # Mostrar estadísticas de cache si hay datos
    if hasattr(CotacaoService, 'cotizacoes_cache'):
        cache_items = len(getattr(CotacaoService, 'cotizacoes_cache', {}))
        if cache_items > 0:
            st.sidebar.info(f"📊 Cache: {cache_items} cotizaciones almacenadas")