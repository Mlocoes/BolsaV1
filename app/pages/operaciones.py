"""
Página de Operaciones

Esta página permite registrar operaciones de compra y venta de activos
y ver el histórico de operaciones realizadas.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from ..services import AtivoService, OperacaoService


def show_operaciones_page():
    """Muestra la página de registro de operaciones"""
    st.header("💼 Registro de Operaciones")
    
    ativos = AtivoService.listar_ativos()
    if not ativos:
        st.warning("No hay valores registrados. Ve a la sección 'Valores' para añadir algunos.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Nueva Operación")
        with st.form("form_operacao"):
            ativo_selecionado = st.selectbox(
                "Valor",
                options=[(a.id, f"{a.ticker} - {a.nome}") for a in ativos],
                format_func=lambda x: x[1]
            )
            
            data_operacao = st.date_input("Fecha", value=datetime.now())
            tipo_operacao = st.radio("Tipo", ["compra", "venda"], horizontal=True)
            quantidade = st.number_input("Cantidad", min_value=1, value=1, step=1)
            preco = st.number_input("Precio Unitario", min_value=0.01, value=100.00, step=0.01)
            
            # Calcular total
            total = quantidade * preco
            st.info(f"💰 **Total de la operación: ${total:,.2f}**")
            
            submitted = st.form_submit_button("Registrar Operación", type="primary")
            
            if submitted:
                if OperacaoService.registrar_operacao(
                    ativo_id=ativo_selecionado[0],
                    data=datetime.combine(data_operacao, datetime.min.time()),
                    tipo=tipo_operacao,
                    quantidade=quantidade,
                    preco=preco
                ):
                    st.rerun()
    
    with col2:
        st.subheader("📊 Resumen")
        operacoes = OperacaoService.listar_operacoes()
        total_operacoes = len(operacoes)
        
        # Calcular estadísticas
        if operacoes:
            compras = [op for op in operacoes if op.tipo == 'compra']
            vendas = [op for op in operacoes if op.tipo == 'venda']
            
            total_compras = len(compras)
            total_vendas = len(vendas)
            valor_compras = sum(op.quantidade * float(op.preco) for op in compras)
            valor_vendas = sum(op.quantidade * float(op.preco) for op in vendas)
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric("Total Operaciones", total_operacoes)
                st.metric("Compras", total_compras)
                st.metric("Valor Compras", f"${valor_compras:,.2f}")
                
            with col2b:
                st.metric("Vendas", total_vendas)
                st.metric("Valor Vendas", f"${valor_vendas:,.2f}")
                if valor_compras > 0:
                    resultado = valor_vendas - valor_compras
                    st.metric("Resultado", f"${resultado:,.2f}", 
                             delta=f"{(resultado/valor_compras)*100:.2f}%")
        else:
            st.metric("Total Operaciones", 0)
    
    st.markdown("---")
    st.subheader("📜 Histórico de Operaciones")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ativo_filtro = st.selectbox(
            "Filtrar por activo",
            options=[None] + [a.id for a in ativos],
            format_func=lambda x: "Todos" if x is None else next((a.ticker for a in ativos if a.id == x), "N/A"),
            index=0
        )
    
    with col2:
        tipo_filtro = st.selectbox(
            "Filtrar por tipo",
            options=["todos", "compra", "venda"]
        )
    
    with col3:
        limite = st.number_input("Mostrar últimas", min_value=10, max_value=500, value=50, step=10)
    
    # Obtener operaciones filtradas
    if ativo_filtro:
        operacoes = OperacaoService.listar_operacoes(ativo_id=ativo_filtro)
    else:
        operacoes = OperacaoService.listar_operacoes()
    
    # Filtrar por tipo
    if tipo_filtro != "todos":
        operacoes = [op for op in operacoes if op.tipo == tipo_filtro]
    
    if operacoes:
        data_ops = []
        for op in operacoes[:limite]:  # Límite de registros
            ativo = next((a for a in ativos if a.id == op.ativo_id), None)
            
            # Color para el tipo
            tipo_icon = "🟢" if op.tipo == "compra" else "🔴"
            
            data_ops.append({
                'Fecha': op.data.strftime('%Y-%m-%d'),
                'Ticker': ativo.ticker if ativo else 'N/A',
                'Tipo': f"{tipo_icon} {op.tipo.upper()}",
                'Cantidad': f"{op.quantidade:,}",
                'Precio Unit.': f"${float(op.preco):.2f}",
                'Total': f"${op.quantidade * float(op.preco):,.2f}"
            })
        
        df_ops = pd.DataFrame(data_ops)
        st.dataframe(df_ops, use_container_width=True)
        
        # Estadísticas de las operaciones mostradas
        if data_ops:
            total_mostrado = len(data_ops)
            valor_total_mostrado = sum(op.quantidade * float(op.preco) for op in operacoes[:limite])
            
            st.info(f"📊 Mostrando {total_mostrado} operaciones por un valor total de ${valor_total_mostrado:,.2f}")
    else:
        st.info("No hay operaciones que coincidan con los filtros seleccionados.")
    
    # Información adicional
    st.markdown("---")
    st.info("""
    💡 **Información sobre las operaciones:**
    - Las operaciones se registran con validación de saldo para ventas
    - Se actualizan automáticamente las posiciones al registrar operaciones
    - Se puede filtrar el histórico por activo, tipo y cantidad de registros
    - 🟢 Compra | 🔴 Venta
    """)