"""
Página de Posiciones

Esta página muestra las posiciones consolidadas del portfolio, incluyendo
resultados, rentabilidades y métricas de performance.
"""

import streamlit as st
import pandas as pd
from ..services import AtivoService, PosicaoService


def show_posiciones_page():
    """Muestra la página de posiciones consolidadas"""
    st.header("📊 Posiciones Consolidadas")
    
    if st.button("🔄 Actualizar Posiciones", type="primary"):
        if PosicaoService.atualizar_todas_posicoes():
            st.success("✅ Todas las posiciones actualizadas correctamente")
        else:
            st.warning("⚠️ Algunas posiciones no se pudieron actualizar")
        st.rerun()
    
    st.markdown("---")
    
    # Obtener resumen del portfolio
    resumo = PosicaoService.obter_resumo_portfolio()
    posicoes = PosicaoService.listar_posicoes()
    
    if posicoes:
        # Resumen general del portfolio
        st.subheader("💰 Resumen del Portfolio")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Invertido", f"${resumo['valor_total_investido']:,.2f}")
        
        with col2:
            st.metric("Valor Actual", f"${resumo['valor_atual_portfolio']:,.2f}")
        
        with col3:
            resultado_color = "normal"
            if resumo['resultado_total_acumulado'] > 0:
                resultado_color = "normal"
            elif resumo['resultado_total_acumulado'] < 0:
                resultado_color = "inverse"
                
            st.metric(
                "Resultado Total", 
                f"${resumo['resultado_total_acumulado']:,.2f}",
                delta=f"{resumo['percentual_resultado']:.2f}%"
            )
        
        with col4:
            st.metric("Posiciones Activas", resumo['total_ativos'])
        
        # Resultado del día
        if resumo['resultado_total_dia'] != 0:
            with st.container():
                if resumo['resultado_total_dia'] > 0:
                    st.success(f"📈 Ganancia del día: ${resumo['resultado_total_dia']:,.2f}")
                else:
                    st.error(f"📉 Pérdida del día: ${resumo['resultado_total_dia']:,.2f}")
        
        st.markdown("---")
        
        # Tabla detallada de posiciones
        st.subheader("📋 Detalle de Posiciones")
        
        data_pos = []
        ativos = AtivoService.listar_ativos(apenas_ativos=False)  # Incluir inactivos para histórico
        
        for pos in posicoes:
            ativo = next((a for a in ativos if a.id == pos.ativo_id), None)
            
            if ativo:
                financeiro_compra = float(pos.quantidade_total) * float(pos.preco_medio)
                financeiro_atual = float(pos.quantidade_total) * float(pos.preco_atual)
                rentabilidad = (float(pos.resultado_acumulado) / financeiro_compra * 100) if financeiro_compra > 0 else 0
                
                # Íconos para resultados
                resultado_icon = "🟢" if float(pos.resultado_acumulado) >= 0 else "🔴"
                dia_icon = "📈" if float(pos.resultado_dia) >= 0 else "📉"
                
                data_pos.append({
                    'Ticker': ativo.ticker,
                    'Nombre': ativo.nome or ativo.ticker,
                    'Cantidad': f"{pos.quantidade_total:,}",
                    'Precio Medio': f"${float(pos.preco_medio):.2f}",
                    'Precio Actual': f"${float(pos.preco_atual):.2f}",
                    'Invertido': f"${financeiro_compra:,.2f}",
                    'Valor Actual': f"${financeiro_atual:,.2f}",
                    'Resultado Día': f"{dia_icon} ${float(pos.resultado_dia):,.2f}",
                    'Resultado Total': f"{resultado_icon} ${float(pos.resultado_acumulado):,.2f}",
                    'Rentabilidad': f"{rentabilidad:.2f}%",
                    'Estado': '✅ Activo' if ativo.ativo else '⏸️ Inactivo'
                })
        
        if data_pos:
            df_pos = pd.DataFrame(data_pos)
            
            # Ordenar por resultado acumulado (mejores primero)
            df_pos['_resultado_sort'] = [float(pos.resultado_acumulado) for pos in posicoes]
            df_pos = df_pos.sort_values('_resultado_sort', ascending=False)
            df_pos = df_pos.drop('_resultado_sort', axis=1)
            
            st.dataframe(df_pos, use_container_width=True)
            
            # Análisis adicional
            st.markdown("---")
            st.subheader("📊 Análisis del Portfolio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top performers
                posicoes_ordenadas = sorted(posicoes, key=lambda p: float(p.resultado_acumulado), reverse=True)
                
                st.markdown("**🏆 Mejores Performers:**")
                for i, pos in enumerate(posicoes_ordenadas[:3]):
                    ativo = next((a for a in ativos if a.id == pos.ativo_id), None)
                    if ativo:
                        financeiro_compra = float(pos.quantidade_total) * float(pos.preco_medio)
                        rentabilidad = (float(pos.resultado_acumulado) / financeiro_compra * 100) if financeiro_compra > 0 else 0
                        
                        medal = ["🥇", "🥈", "🥉"][i]
                        st.write(f"{medal} **{ativo.ticker}**: {rentabilidad:.2f}% (${float(pos.resultado_acumulado):,.2f})")
            
            with col2:
                # Distribución del portfolio
                st.markdown("**💼 Distribución por Valor:**")
                
                for pos in sorted(posicoes, key=lambda p: float(p.quantidade_total) * float(p.preco_atual), reverse=True)[:5]:
                    ativo = next((a for a in ativos if a.id == pos.ativo_id), None)
                    if ativo:
                        valor_atual = float(pos.quantidade_total) * float(pos.preco_atual)
                        porcentaje = (valor_atual / resumo['valor_atual_portfolio'] * 100) if resumo['valor_atual_portfolio'] > 0 else 0
                        
                        st.write(f"📊 **{ativo.ticker}**: {porcentaje:.1f}% (${valor_atual:,.2f})")
        
        # Información adicional
        st.markdown("---")
        st.info("""
        💡 **Información sobre las posiciones:**
        - Las posiciones se calculan automáticamente basadas en las operaciones registradas
        - Los precios actuales se obtienen de Yahoo Finance en tiempo real
        - La rentabilidad se calcula como: (Precio Actual - Precio Medio) / Precio Medio
        - 🟢 Ganancia | 🔴 Pérdida | 📈 Subida del día | 📉 Bajada del día
        """)
        
        # Botón para actualizar precios diarios
        if st.button("💾 Guardar Precios Diarios", help="Guarda los precios actuales en la base de datos para históricos"):
            from ..services import CotacaoService
            
            guardados = 0
            for pos in posicoes:
                ativo = next((a for a in ativos if a.id == pos.ativo_id), None)
                if ativo:
                    if CotacaoService.salvar_preco_diario(ativo.id, ativo.ticker):
                        guardados += 1
            
            st.success(f"✅ Precios guardados para {guardados} activos")
        
    else:
        st.info("📈 No hay posiciones abiertas. Registra operaciones de compra para crear posiciones.")
        
        # Sugerencias para empezar
        st.markdown("---")
        st.markdown("**🚀 Para empezar:**")
        st.markdown("""
        1. Ve a la sección **Valores** para agregar activos
        2. Visita **Operaciones** para registrar compras
        3. Las posiciones se crearán automáticamente
        """)
        
        # Mostrar si hay operaciones pero no posiciones
        from ..services import OperacaoService
        operacoes = OperacaoService.listar_operacoes()
        if operacoes:
            st.warning("⚠️ Hay operaciones registradas pero no posiciones activas. Verifica que las operaciones estén balanceadas.")