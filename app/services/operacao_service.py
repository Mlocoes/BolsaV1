"""
Servicio de Operaciones - Multi-Usuario (FASE 3)

Este módulo contiene la lógica de negocio para el manejo de operaciones
de compra y venta de activos financieros con soporte multi-usuario.
"""

import logging
import streamlit as st
from datetime import datetime
from typing import List, Optional
from ..models import SessionLocal, Operacao, Posicao
from ..utils.logging_config import get_logger
from .base_service import BaseService

# Configurar logger
logger = get_logger(__name__)


class OperacaoService(BaseService):
    """Servicio para gestión de operaciones financieras con soporte multi-usuario"""
    
    @staticmethod
    def registrar_operacao(ativo_id: int, data: datetime, tipo: str, quantidade: int, preco: float) -> bool:
        """
        Registra una operación de compra o venta para el usuario actual
        
        Args:
            ativo_id: ID del activo (debe pertenecer al usuario)
            data: Fecha de la operación
            tipo: Tipo de operación ('compra' o 'venda')
            quantidade: Cantidad de acciones
            preco: Precio por acción
            
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        session = SessionLocal()
        
        try:
            # Obtener usuario actual
            user_id = OperacaoService._get_current_user_id()
            
            logger.info(f"Usuario {user_id} iniciando registro de operação: ativo_id={ativo_id}, tipo={tipo}, quantidade={quantidade}, preco={preco}")
            
            # Verificar que el activo pertenece al usuario
            from ..models import Ativo
            ativo = session.query(Ativo).filter(
                Ativo.id == ativo_id,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                logger.warning(f"Usuario {user_id} tentou operar ativo inexistente ou de outro usuario: {ativo_id}")
                st.error("❌ Error: Activo no encontrado en tu cartera")
                return False
            
            # VALIDACIÓN: Verificar saldo suficiente para ventas
            if tipo == 'venda':
                posicao_atual = session.query(Posicao).filter(
                    Posicao.ativo_id == ativo_id,
                    Posicao.user_id == user_id
                ).first()
                
                if not posicao_atual:
                    logger.warning(f"Usuario {user_id} tentou venda sem posição: ativo_id={ativo_id}")
                    st.error("❌ Error: No tienes posición en este activo para vender")
                    return False
                
                if posicao_atual.quantidade_total < quantidade:
                    logger.warning(f"Usuario {user_id} tentou venda com saldo insuficiente: ativo_id={ativo_id}, saldo={posicao_atual.quantidade_total}, tentativa={quantidade}")
                    st.error(f"❌ Error: Saldo insuficiente. Tienes {posicao_atual.quantidade_total} acciones, intentas vender {quantidade}")
                    return False
            
            # Crear nueva operación para el usuario
            nova_operacao = Operacao(
                ativo_id=ativo_id,
                data=data.date(),
                tipo=tipo,
                quantidade=quantidade,
                preco=preco,
                user_id=user_id  # Asignar al usuario actual
            )
            session.add(nova_operacao)
            session.commit()
            
            logger.info(f"Usuario {user_id} registrou operação com sucesso para ativo {ativo_id}")
            
            # Actualizar posición del usuario (importar aquí para evitar circular)
            from .posicao_service import PosicaoService
            PosicaoService.atualizar_posicao(ativo_id)
            
            st.success(f"✅ Operación de {tipo} registrada correctamente en tu cartera")
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
        Lista operaciones del usuario actual, opcionalmente filtradas por activo
        
        Args:
            ativo_id: ID del activo para filtrar (opcional, debe pertenecer al usuario)
            
        Returns:
            List[Operacao]: Lista de operaciones del usuario
        """
        session = SessionLocal()
        try:
            user_id = OperacaoService._get_current_user_id()
            
            # Query base filtrada por usuario
            query = session.query(Operacao).filter(
                Operacao.user_id == user_id
            ).order_by(Operacao.data.desc())
            
            # Filtrar por activo si se especifica
            if ativo_id:
                # Verificar que el activo pertenece al usuario
                from ..models import Ativo
                ativo = session.query(Ativo).filter(
                    Ativo.id == ativo_id,
                    Ativo.user_id == user_id
                ).first()
                
                if ativo:
                    query = query.filter(Operacao.ativo_id == ativo_id)
                else:
                    logger.warning(f"Usuario {user_id} tentou listar operações de ativo inexistente: {ativo_id}")
                    return []
            
            operacoes = query.all()
            logger.info(f"Usuario {user_id} listou {len(operacoes)} operações")
            return operacoes
            
        except Exception as e:
            logger.error(f"Erro ao listar operações: {e}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def obter_operacao_por_id(operacao_id: int) -> Optional[Operacao]:
        """
        Obtiene una operación por su ID, verificando que pertenezca al usuario actual
        
        Args:
            operacao_id: ID de la operación
            
        Returns:
            Optional[Operacao]: La operación si existe y pertenece al usuario, None en caso contrario
        """
        session = SessionLocal()
        try:
            user_id = OperacaoService._get_current_user_id()
            
            return session.query(Operacao).filter(
                Operacao.id == operacao_id,
                Operacao.user_id == user_id
            ).first()
            
        except Exception as e:
            logger.error(f"Erro ao obter operação por ID {operacao_id}: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def eliminar_operacao(operacao_id: int) -> bool:
        """
        Elimina una operación del usuario actual y actualiza las posiciones
        
        Args:
            operacao_id: ID de la operación a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        session = SessionLocal()
        
        try:
            user_id = OperacaoService._get_current_user_id()
            
            logger.info(f"Usuario {user_id} tentando eliminar operação: {operacao_id}")
            
            # Buscar la operación del usuario
            operacao = session.query(Operacao).filter(
                Operacao.id == operacao_id,
                Operacao.user_id == user_id
            ).first()
            
            if not operacao:
                st.error(f"❌ Operación {operacao_id} no encontrada en tu cartera")
                return False
            
            ativo_id = operacao.ativo_id
            
            # Eliminar la operación
            session.delete(operacao)
            session.commit()
            
            logger.info(f"Usuario {user_id} eliminó operação {operacao_id} com sucesso")
            
            # Actualizar posición del usuario
            from .posicao_service import PosicaoService
            PosicaoService.atualizar_posicao(ativo_id)
            
            st.success(f"✅ Operación eliminada correctamente de tu cartera")
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
        Obtiene un resumen de las operaciones de un activo del usuario actual
        
        Args:
            ativo_id: ID del activo (debe pertenecer al usuario)
            
        Returns:
            dict: Resumen con totales de compra y venta del usuario
        """
        session = SessionLocal()
        try:
            user_id = OperacaoService._get_current_user_id()
            
            # Verificar que el activo pertenece al usuario
            from ..models import Ativo
            ativo = session.query(Ativo).filter(
                Ativo.id == ativo_id,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                logger.warning(f"Usuario {user_id} tentou obter resumo de ativo inexistente: {ativo_id}")
                return self._resumo_vacio()
            
            # Obtener operaciones del usuario para este activo
            operacoes = session.query(Operacao).filter(
                Operacao.ativo_id == ativo_id,
                Operacao.user_id == user_id
            ).all()
            
            total_compras = sum(op.quantidade for op in operacoes if op.tipo == 'compra')
            total_vendas = sum(op.quantidade for op in operacoes if op.tipo == 'venda')
            valor_total_compras = sum(op.quantidade * float(op.preco) for op in operacoes if op.tipo == 'compra')
            valor_total_vendas = sum(op.quantidade * float(op.preco) for op in operacoes if op.tipo == 'venda')
            
            logger.info(f"Usuario {user_id} obteve resumo de {len(operacoes)} operações para ativo {ativo_id}")
            
            return {
                'total_compras': total_compras,
                'total_vendas': total_vendas,
                'quantidade_atual': total_compras - total_vendas,
                'valor_total_compras': valor_total_compras,
                'valor_total_vendas': valor_total_vendas,
                'preco_medio_compra': valor_total_compras / total_compras if total_compras > 0 else 0,
                'preco_medio_venda': valor_total_vendas / total_vendas if total_vendas > 0 else 0,
                'total_operacoes': len(operacoes),
                'user_id': user_id,
                'ativo_id': ativo_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de operações para ativo {ativo_id}: {e}")
            return OperacaoService._resumo_vazio()
        finally:
            session.close()
    
    @staticmethod
    def _resumo_vazio() -> dict:
        """
        Retorna um resumo vazio padrão
        
        Returns:
            dict: Resumo com valores zerados
        """
        return {
            'total_compras': 0,
            'total_vendas': 0,
            'quantidade_atual': 0,
            'valor_total_compras': 0,
            'valor_total_vendas': 0,
            'preco_medio_compra': 0,
            'preco_medio_venda': 0,
            'total_operacoes': 0,
            'user_id': None,
            'ativo_id': None
        }
    
    @staticmethod
    def get_user_operations_count(user_id: int = None) -> int:
        """
        Obtiene el número total de operaciones de un usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            int: Número de operaciones del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = OperacaoService._get_current_user_id()
            
            count = session.query(Operacao).filter(
                Operacao.user_id == user_id
            ).count()
            
            logger.info(f"Usuario {user_id} tem {count} operações registradas")
            return count
            
        except Exception as e:
            logger.error(f"Erro ao contar operações do usuario {user_id}: {e}")
            return 0
        finally:
            session.close()
    
    @staticmethod
    def get_user_statistics(user_id: int = None) -> dict:
        """
        Obtiene estadísticas completas de operaciones de un usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            dict: Estadísticas del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = OperacaoService._get_current_user_id()
            
            operacoes = session.query(Operacao).filter(
                Operacao.user_id == user_id
            ).all()
            
            total_operacoes = len(operacoes)
            total_compras = sum(1 for op in operacoes if op.tipo == 'compra')
            total_vendas = sum(1 for op in operacoes if op.tipo == 'venda')
            
            valor_total_operado = sum(
                op.quantidade * float(op.preco) for op in operacoes
            )
            
            # Ativos únicos operados
            ativos_operados = len(set(op.ativo_id for op in operacoes))
            
            # Primeira e última operação
            primeira_operacao = min(op.data for op in operacoes) if operacoes else None
            ultima_operacao = max(op.data for op in operacoes) if operacoes else None
            
            return {
                'total_operacoes': total_operacoes,
                'total_compras': total_compras,
                'total_vendas': total_vendas,
                'valor_total_operado': valor_total_operado,
                'ativos_operados': ativos_operados,
                'primeira_operacao': primeira_operacao,
                'ultima_operacao': ultima_operacao,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do usuario {user_id}: {e}")
            return {
                'total_operacoes': 0,
                'total_compras': 0,
                'total_vendas': 0,
                'valor_total_operado': 0,
                'ativos_operados': 0,
                'primeira_operacao': None,
                'ultima_operacao': None,
                'user_id': user_id
            }
        finally:
            session.close()