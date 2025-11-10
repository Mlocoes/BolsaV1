"""
Servicio de Posiciones - Multi-Usuario (FASE 3)

Este módulo contiene la lógica de negocio para el manejo de posiciones
consolidadas de activos financieros con soporte multi-usuario.
"""

import logging
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from ..models import SessionLocal, Posicao, Operacao, Ativo, PrecoDiario
from ..utils.auth import StreamlitAuth
from ..utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)


class PosicaoService:
    """Servicio para gestión de posiciones de activos financieros con soporte multi-usuario"""
    
    @staticmethod
    def _get_current_user_id() -> int:
        """
        Obtiene el ID del usuario actual autenticado
        
        Returns:
            int: ID del usuario actual
            
        Raises:
            Exception: Si no hay usuario autenticado
        """
        if not StreamlitAuth.is_authenticated():
            raise Exception("Usuario no autenticado")
        
        user = StreamlitAuth.get_current_user()
        if not user:
            raise Exception("No se pudo obtener información del usuario")
        
        return user['id']
    
    @staticmethod
    def atualizar_posicao(ativo_id: int, user_id: int = None) -> bool:
        """
        Actualiza la posición consolidada de un activo para un usuario específico
        
        Args:
            ativo_id: ID del activo
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        session = SessionLocal()
        
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            logger.info(f"Atualizando posição para ativo_id={ativo_id}, usuario={user_id}")
            
            # Verificar que el activo pertenece al usuario
            ativo = session.query(Ativo).filter(
                Ativo.id == ativo_id,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                logger.warning(f"Ativo {ativo_id} não pertence ao usuario {user_id}")
                return False
            
            # Obtener todas las operaciones del activo del usuario
            operacoes = session.query(Operacao).filter(
                Operacao.ativo_id == ativo_id,
                Operacao.user_id == user_id
            ).all()
            
            logger.info(f"Encontradas {len(operacoes)} operações para ativo {ativo_id} usuario {user_id}")
            
            quantidade_total = 0
            valor_total = 0
            
            for op in operacoes:
                if op.tipo == 'compra':
                    quantidade_total += op.quantidade
                    valor_total += op.quantidade * float(op.preco)
                else:  # venda
                    quantidade_total -= op.quantidade
                    valor_total -= op.quantidade * float(op.preco)
            
            preco_medio = valor_total / quantidade_total if quantidade_total > 0 else 0
            logger.info(f"Posição calculada para usuario {user_id}: quantidade={quantidade_total}, preço_médio={preco_medio:.4f}")
            
            # Obtener precio actual
            from .cotacao_service import CotacaoService
            cotacao = CotacaoService.obter_cotacao_atual(ativo.ticker)
            preco_atual = cotacao['preco_atual'] if cotacao else 0
            
            if preco_atual == 0:
                logger.warning(f"Preço atual não disponível para {ativo.ticker}, usando 0")
            
            # Calcular resultados
            resultado_acumulado = (preco_atual - preco_medio) * quantidade_total if quantidade_total > 0 else 0
            
            # Obtener precio de ayer para resultado del día (del usuario)
            ontem = datetime.now().date() - timedelta(days=1)
            preco_ontem = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo_id,
                PrecoDiario.user_id == user_id,
                PrecoDiario.data == ontem
            ).first()
            
            resultado_dia = (preco_atual - float(preco_ontem.preco_fechamento)) * quantidade_total if preco_ontem and quantidade_total > 0 else 0
            
            # Actualizar o crear posición del usuario
            posicao = session.query(Posicao).filter(
                Posicao.ativo_id == ativo_id,
                Posicao.user_id == user_id
            ).first()
            
            if posicao:
                logger.info(f"Atualizando posição existente para {ativo.ticker} usuario {user_id}")
                posicao.quantidade_total = quantidade_total
                posicao.preco_medio = preco_medio
                posicao.preco_atual = preco_atual
                posicao.resultado_dia = resultado_dia
                posicao.resultado_acumulado = resultado_acumulado
            else:
                logger.info(f"Criando nova posição para {ativo.ticker} usuario {user_id}")
                nova_posicao = Posicao(
                    ativo_id=ativo_id,
                    quantidade_total=quantidade_total,
                    preco_medio=preco_medio,
                    preco_atual=preco_atual,
                    resultado_dia=resultado_dia,
                    resultado_acumulado=resultado_acumulado,
                    user_id=user_id  # Asignar al usuario
                )
                session.add(nova_posicao)
            
            session.commit()
            logger.info(f"Posição atualizada com sucesso para {ativo.ticker} usuario {user_id}: resultado_acumulado={resultado_acumulado:.2f}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao atualizar posição do ativo {ativo_id}: {e}", exc_info=True)
            st.error(f"❌ Error al actualizar posición: {e}")
            return False
        finally:
            session.close()
            
            session.commit()
            logger.info(f"Posição atualizada com sucesso para {ativo.ticker}: resultado_acumulado={resultado_acumulado:.2f}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao atualizar posição do ativo {ativo_id}: {e}", exc_info=True)
            st.error(f"❌ Error al actualizar posición: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def listar_posicoes(user_id: int = None) -> List[Posicao]:
        """
        Lista todas las posiciones con cantidad > 0 del usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            List[Posicao]: Lista de posiciones activas del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            posicoes = session.query(Posicao).filter(
                Posicao.quantidade_total > 0,
                Posicao.user_id == user_id
            ).all()
            
            logger.info(f"Usuario {user_id} listou {len(posicoes)} posições ativas")
            return posicoes
            
        except Exception as e:
            logger.error(f"Erro ao listar posições: {e}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def obter_posicao_por_ativo(ativo_id: int, user_id: int = None) -> Optional[Posicao]:
        """
        Obtiene la posición de un activo específico del usuario
        
        Args:
            ativo_id: ID del activo
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            Optional[Posicao]: La posición si existe y pertenece al usuario, None en caso contrario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            return session.query(Posicao).filter(
                Posicao.ativo_id == ativo_id,
                Posicao.user_id == user_id
            ).first()
            
        except Exception as e:
            logger.error(f"Erro ao obter posição por ativo {ativo_id}: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def atualizar_todas_posicoes(user_id: int = None) -> bool:
        """
        Actualiza todas las posiciones con precios actuales del usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            bool: True si todas se actualizaron correctamente
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            # Obtener todas las posiciones del usuario
            posicoes = session.query(Posicao).filter(
                Posicao.user_id == user_id
            ).all()
            
            total_atualizadas = 0
            
            for posicao in posicoes:
                try:
                    PosicaoService.atualizar_posicao(posicao.ativo_id, user_id)
                    total_atualizadas += 1
                except Exception as e:
                    logger.error(f"Erro ao atualizar posição {posicao.ativo_id} usuario {user_id}: {e}")
                    continue
            
            logger.info(f"Usuario {user_id}: atualizadas {total_atualizadas} de {len(posicoes)} posições")
            return total_atualizadas == len(posicoes)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar todas as posições: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def obter_resumo_portfolio(user_id: int = None) -> dict:
        """
        Obtiene un resumen completo del portfolio del usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            dict: Resumen del portfolio con valores totales del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            posicoes = session.query(Posicao).filter(
                Posicao.quantidade_total > 0,
                Posicao.user_id == user_id
            ).all()
            
            valor_total_investido = 0
            valor_atual_portfolio = 0
            resultado_total_dia = 0
            resultado_total_acumulado = 0
            total_ativos = len(posicoes)
            
            for posicao in posicoes:
                valor_investido = float(posicao.preco_medio) * posicao.quantidade_total
                valor_atual = float(posicao.preco_atual) * posicao.quantidade_total
                
                valor_total_investido += valor_investido
                valor_atual_portfolio += valor_atual
                resultado_total_dia += float(posicao.resultado_dia)
                resultado_total_acumulado += float(posicao.resultado_acumulado)
            
            percentual_resultado = (resultado_total_acumulado / valor_total_investido * 100) if valor_total_investido > 0 else 0
            
            logger.info(f"Resumo portfolio usuario {user_id}: {total_ativos} ativos, valor atual: {valor_atual_portfolio:.2f}")
            
            return {
                'total_ativos': total_ativos,
                'valor_total_investido': valor_total_investido,
                'valor_atual_portfolio': valor_atual_portfolio,
                'resultado_total_dia': resultado_total_dia,
                'resultado_total_acumulado': resultado_total_acumulado,
                'percentual_resultado': percentual_resultado,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo do portfolio: {e}")
            return {
                'total_ativos': 0,
                'valor_total_investido': 0,
                'valor_atual_portfolio': 0,
                'resultado_total_dia': 0,
                'resultado_total_acumulado': 0,
                'percentual_resultado': 0,
                'user_id': user_id
            }
        finally:
            session.close()
    
    @staticmethod
    def eliminar_posicao(ativo_id: int, user_id: int = None) -> bool:
        """
        Elimina una posición del usuario (solo si cantidad = 0)
        
        Args:
            ativo_id: ID del activo
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            bool: True si se eliminó correctamente
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            posicao = session.query(Posicao).filter(
                Posicao.ativo_id == ativo_id,
                Posicao.user_id == user_id
            ).first()
            
            if not posicao:
                return True  # Ya no existe
            
            if posicao.quantidade_total > 0:
                st.error("❌ No se puede eliminar posición con cantidad > 0")
                return False
            
            session.delete(posicao)
            session.commit()
            
            logger.info(f"Posição eliminada para ativo {ativo_id} usuario {user_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao eliminar posição: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_user_positions_count(user_id: int = None) -> int:
        """
        Obtiene el número total de posiciones activas de un usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            int: Número de posiciones activas del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            count = session.query(Posicao).filter(
                Posicao.user_id == user_id,
                Posicao.quantidade_total > 0
            ).count()
            
            logger.info(f"Usuario {user_id} tem {count} posições ativas")
            return count
            
        except Exception as e:
            logger.error(f"Erro ao contar posições do usuario {user_id}: {e}")
            return 0
        finally:
            session.close()
    
    @staticmethod
    def get_user_statistics(user_id: int = None) -> dict:
        """
        Obtiene estadísticas completas de posiciones de un usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            dict: Estadísticas del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = PosicaoService._get_current_user_id()
            
            # Posiciones activas
            posicoes_ativas = session.query(Posicao).filter(
                Posicao.user_id == user_id,
                Posicao.quantidade_total > 0
            ).all()
            
            # Posiciones totales (incluyendo cero)
            total_posicoes = session.query(Posicao).filter(
                Posicao.user_id == user_id
            ).count()
            
            # Mejor y peor posición
            melhor_resultado = max(
                (float(p.resultado_acumulado) for p in posicoes_ativas), 
                default=0
            )
            
            pior_resultado = min(
                (float(p.resultado_acumulado) for p in posicoes_ativas), 
                default=0
            )
            
            # Portfolio summary
            resumo = PosicaoService.obter_resumo_portfolio(user_id)
            
            return {
                'posicoes_ativas': len(posicoes_ativas),
                'total_posicoes': total_posicoes,
                'valor_portfolio': resumo['valor_atual_portfolio'],
                'resultado_acumulado': resumo['resultado_total_acumulado'],
                'resultado_dia': resumo['resultado_total_dia'],
                'percentual_resultado': resumo['percentual_resultado'],
                'melhor_resultado': melhor_resultado,
                'pior_resultado': pior_resultado,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do usuario {user_id}: {e}")
            return {
                'posicoes_ativas': 0,
                'total_posicoes': 0,
                'valor_portfolio': 0,
                'resultado_acumulado': 0,
                'resultado_dia': 0,
                'percentual_resultado': 0,
                'melhor_resultado': 0,
                'pior_resultado': 0,
                'user_id': user_id
            }
        finally:
            session.close()