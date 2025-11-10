"""
Página de Valores

Esta página permite gestionar los activos financieros: agregar, eliminar,
desactivar y reactivar valores.
"""

import streamlit as st
import pandas as pd
from ..services import AtivoService


def show_valores_page():
    """Muestra la página de gestión de valores"""
    st.header("📈 Gestión de Valores")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("➕ Añadir Nuevo Valor")
        with st.form("form_nuevo_ativo"):
            ticker_input = st.text_input("Ticker (ej: AAPL, MSFT, GOOGL)", max_chars=10)
            nome_input = st.text_input("Nombre (opcional)")
            submitted = st.form_submit_button("Añadir Valor")
            
            if submitted and ticker_input:
                if AtivoService.adicionar_ativo(ticker_input, nome_input):
                    st.rerun()
    
    with col2:
        st.subheader("💡 Ejemplos de Tickers")
        st.markdown("""
        - **AAPL** - Apple
        - **MSFT** - Microsoft
        - **GOOGL** - Alphabet/Google
        - **TSLA** - Tesla
        - **AMZN** - Amazon
        - **META** - Meta/Facebook
        """)
    
    st.markdown("---")
    st.subheader("📊 Valores Registrados")
    
    ativos = AtivoService.listar_ativos()
    st.write(f"✅ Sistema funcionando: {len(ativos)} activos disponibles")  # Info line
    
    if ativos:
        # Mostrar tabla de activos
        data = []
        for ativo in ativos:
            data.append({
                'ID': ativo.id,
                'Ticker': ativo.ticker,
                'Nombre': ativo.nome,
                'Activo': '✅' if ativo.ativo else '❌'
            })
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Sección de gestión de activos - VERSIÓN COMPLETA
        st.markdown("---")
        st.subheader("🔧 Gestión de Activos")
        
        # Crear tres columnas para las diferentes opciones
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🗑️ Eliminar Activo**")
            with st.form("form_eliminar_ativo"):
                ticker_eliminar = st.selectbox(
                    "Seleccionar activo para eliminar:",
                    options=[ativo.ticker for ativo in ativos],
                    help="⚠️ CUIDADO: Esto eliminará TODOS los datos relacionados"
                )
                submitted_eliminar = st.form_submit_button("🗑️ Eliminar", type="secondary")
                
                if submitted_eliminar and ticker_eliminar:
                    if AtivoService.eliminar_ativo(ticker_eliminar):
                        st.rerun()
        
        with col2:
            st.markdown("**⏸️ Desactivar Activo**")
            ativos_activos = [a for a in ativos if a.ativo]
            if ativos_activos:
                with st.form("form_desactivar_ativo"):
                    ticker_desactivar = st.selectbox(
                        "Seleccionar activo para desactivar:",
                        options=[ativo.ticker for ativo in ativos_activos],
                        help="💡 Oculta el activo pero conserva los datos"
                    )
                    submitted_desactivar = st.form_submit_button("⏸️ Desactivar", type="secondary")
                    
                    if submitted_desactivar and ticker_desactivar:
                        if AtivoService.desactivar_ativo(ticker_desactivar):
                            st.rerun()
            else:
                st.info("No hay activos activos para desactivar")
        
        with col3:
            st.markdown("**▶️ Reactivar Activo**")
            ativos_inativos = [a for a in AtivoService.listar_ativos(apenas_ativos=False) if not a.ativo]
            if ativos_inativos:
                with st.form("form_reactivar_ativo"):
                    ticker_reactivar = st.selectbox(
                        "Seleccionar activo para reactivar:",
                        options=[ativo.ticker for ativo in ativos_inativos],
                        help="▶️ Volver a mostrar activo desactivado"
                    )
                    submitted_reactivar = st.form_submit_button("▶️ Reactivar", type="primary")
                    
                    if submitted_reactivar and ticker_reactivar:
                        if AtivoService.reactivar_ativo(ticker_reactivar):
                            st.rerun()
            else:
                st.info("No hay activos desactivados")
                
        # Información de ayuda
        st.markdown("---")
        st.info("""
        💡 **Opciones de gestión:**
        - **🗑️ Eliminar**: Borra completamente el activo y TODOS sus datos (irreversible)
        - **⏸️ Desactivar**: Oculta el activo pero conserva todos los datos históricos
        - **▶️ Reactivar**: Vuelve a mostrar un activo desactivado
        
        ⚠️ **Importante**: No se pueden eliminar/desactivar activos con posiciones activas.
        """)
        
    else:
        st.info("No hay valores registrados. Añade algunos usando el formulario arriba.")