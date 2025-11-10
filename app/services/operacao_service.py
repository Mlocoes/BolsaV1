"""
Servicio de Operaciones

Este módulo contiene la lógica de negocio para el manejo de operaciones
de compra y venta de activos financieros.
"""

import logging
import streamlit as st
from datetime import datetime
from typing import List, Optional
from ..models import SessionLocal, Operacao, Posicao

# Configurar logger
logger = logging.getLogger(__name__)


class OperacaoService:
    """Servicio para gestión de operaciones financieras"""
    
    @staticmethod
    def registrar_operacao(ativo_id: int, data: datetime, tipo: str, quantidade: int, preco: float) -> bool:
        """
        Registra una operación de compra o venta
        
        Args:
            ativo_id: ID del activo
            data: Fecha de la operación
            tipo: Tipo de operación ('compra' o 'venda')
            quantidade: Cantidad de acciones
            preco: Precio por acción
            
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        session = SessionLocal()
        logger.info(f"Iniciando registro de operação: ativo_id={ativo_id}, tipo={tipo}, quantidade={quantidade}, preco={preco}")
        
        try:
            # VALIDACIÓN: Verificar saldo suficiente para ventas
            if tipo == 'venda':
                posicao_atual = session.query(Posicao).filter(Posicao.ativo_id == ativo_id).first()
                
                if not posicao_atual:
                    logger.warning(f"Tentativa de venda sem posição: ativo_id={ativo_id}")
                    st.error("❌ Error: No tienes posición en este activo para vender")
                    return False
                
                if posicao_atual.quantidade_total < quantidade:
                    logger.warning(f"Tentativa de venda com saldo insuficiente: ativo_id={ativo_id}, saldo={posicao_atual.quantidade_total}, tentativa={quantidade}")
                    st.error(f"❌ Error: Saldo insuficiente. Tienes {posicao_atual.quantidade_total} acciones, intentas vender {quantidade}")
                    return False
            
            nova_operacao = Operacao(
                ativo_id=ativo_id,
                data=data.date(),
                tipo=tipo,
                quantidade=quantidade,
                preco=preco
            )
            session.add(nova_operacao)
            session.commit()
            
            logger.info(f"Operação registrada com sucesso: ID da operação gerada")
            
            # Actualizar posición (importar aquí para evitar circular)
            from .posicao_service import PosicaoService
            PosicaoService.atualizar_posicao(ativo_id)
            
            st.success(f"✅ Operación de {tipo} registrada correctamente")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao registrar operação: {e}", exc_info=True)
            st.error(f"Error al registrar operación: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def listar_operacoes(ativo_id: Optional[int] = None) -> List[Operacao]:
        """
        Lista operaciones, opcionalmente filtradas por activo
        
        Args:
            ativo_id: ID del activo para filtrar (opcional)
            
        Returns:
            List[Operacao]: Lista de operaciones
        """
        session = SessionLocal()
        try:
            query = session.query(Operacao).order_by(Operacao.data.desc())
            if ativo_id:
                query = query.filter(Operacao.ativo_id == ativo_id)
            return query.all()
        finally:
            session.close()
    
    @staticmethod
    def obter_operacao_por_id(operacao_id: int) -> Optional[Operacao]:
        """
        Obtiene una operación por su ID
        
        Args:
            operacao_id: ID de la operación
            
        Returns:
            Optional[Operacao]: La operación si existe, None en caso contrario
        """
        session = SessionLocal()
        try:
            return session.query(Operacao).filter(Operacao.id == operacao_id).first()
        finally:
            session.close()
    
    @staticmethod
    def eliminar_operacao(operacao_id: int) -> bool:
        """
        Elimina una operación y actualiza las posiciones
        
        Args:
            operacao_id: ID de la operación a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        session = SessionLocal()
        logger.info(f"Tentando eliminar operação: {operacao_id}")
        
        try:
            # Buscar la operación
            operacao = session.query(Operacao).filter(Operacao.id == operacao_id).first()
            if not operacao:
                st.error(f"❌ Operación {operacao_id} no encontrada")
                return False
            
            ativo_id = operacao.ativo_id
            
            # Eliminar la operación
            session.delete(operacao)
            session.commit()
            
            logger.info(f"Operação {operacao_id} eliminada com sucesso")
            
            # Actualizar posición
            from .posicao_service import PosicaoService
            PosicaoService.atualizar_posicao(ativo_id)
            
            st.success(f"✅ Operación eliminada correctamente")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao eliminar operação {operacao_id}: {e}", exc_info=True)
            st.error(f"❌ Error al eliminar operación: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def obter_resumo_operacoes(ativo_id: int) -> dict:
        """
        Obtiene un resumen de las operaciones de un activo
        
        Args:
            ativo_id: ID del activo
            
        Returns:
            dict: Resumen con totales de compra y venta
        """
        session = SessionLocal()
        try:
            operacoes = session.query(Operacao).filter(Operacao.ativo_id == ativo_id).all()
            
            total_compras = sum(op.quantidade for op in operacoes if op.tipo == 'compra')
            total_vendas = sum(op.quantidade for op in operacoes if op.tipo == 'venda')
            valor_total_compras = sum(op.quantidade * float(op.preco) for op in operacoes if op.tipo == 'compra')
            valor_total_vendas = sum(op.quantidade * float(op.preco) for op in operacoes if op.tipo == 'venda')
            
            return {
                'total_compras': total_compras,
                'total_vendas': total_vendas,
                'quantidade_atual': total_compras - total_vendas,
                'valor_total_compras': valor_total_compras,
                'valor_total_vendas': valor_total_vendas,
                'preco_medio_compra': valor_total_compras / total_compras if total_compras > 0 else 0,
                'preco_medio_venda': valor_total_vendas / total_vendas if total_vendas > 0 else 0,
                'total_operacoes': len(operacoes)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de operações para ativo {ativo_id}: {e}")
            return {
                'total_compras': 0,
                'total_vendas': 0,
                'quantidade_atual': 0,
                'valor_total_compras': 0,
                'valor_total_vendas': 0,
                'preco_medio_compra': 0,
                'preco_medio_venda': 0,
                'total_operacoes': 0
            }
        finally:
            session.close()