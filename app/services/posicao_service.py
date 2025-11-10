"""
Servicio de Posiciones

Este módulo contiene la lógica de negocio para el manejo de posiciones
consolidadas de activos financieros.
"""

import logging
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from ..models import SessionLocal, Posicao, Operacao, Ativo, PrecoDiario

# Configurar logger
logger = logging.getLogger(__name__)


class PosicaoService:
    """Servicio para gestión de posiciones de activos financieros"""
    
    @staticmethod
    def atualizar_posicao(ativo_id: int) -> bool:
        """
        Actualiza la posición consolidada de un activo
        
        Args:
            ativo_id: ID del activo
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        session = SessionLocal()
        logger.info(f"Atualizando posição para ativo_id={ativo_id}")
        
        try:
            # Obtener todas las operaciones del activo
            operacoes = session.query(Operacao).filter(Operacao.ativo_id == ativo_id).all()
            logger.info(f"Encontradas {len(operacoes)} operações para ativo {ativo_id}")
            
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
            logger.info(f"Posição calculada: quantidade={quantidade_total}, preço_médio={preco_medio:.4f}")
            
            # Obtener precio actual
            ativo = session.query(Ativo).filter(Ativo.id == ativo_id).first()
            if not ativo:
                logger.error(f"Ativo não encontrado: {ativo_id}")
                return False
                
            # Importar aquí para evitar circular
            from .cotacao_service import CotacaoService
            cotacao = CotacaoService.obter_cotacao_atual(ativo.ticker)
            preco_atual = cotacao['preco_atual'] if cotacao else 0
            
            if preco_atual == 0:
                logger.warning(f"Preço atual não disponível para {ativo.ticker}, usando 0")
            
            # Calcular resultados
            resultado_acumulado = (preco_atual - preco_medio) * quantidade_total if quantidade_total > 0 else 0
            
            # Obtener precio de ayer para resultado del día
            ontem = datetime.now().date() - timedelta(days=1)
            preco_ontem = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo_id,
                PrecoDiario.data == ontem
            ).first()
            
            resultado_dia = (preco_atual - float(preco_ontem.preco_fechamento)) * quantidade_total if preco_ontem and quantidade_total > 0 else 0
            
            # Actualizar o crear posición
            posicao = session.query(Posicao).filter(Posicao.ativo_id == ativo_id).first()
            
            if posicao:
                logger.info(f"Atualizando posição existente para {ativo.ticker}")
                posicao.quantidade_total = quantidade_total
                posicao.preco_medio = preco_medio
                posicao.preco_atual = preco_atual
                posicao.resultado_dia = resultado_dia
                posicao.resultado_acumulado = resultado_acumulado
            else:
                logger.info(f"Criando nova posição para {ativo.ticker}")
                nova_posicao = Posicao(
                    ativo_id=ativo_id,
                    quantidade_total=quantidade_total,
                    preco_medio=preco_medio,
                    preco_atual=preco_atual,
                    resultado_dia=resultado_dia,
                    resultado_acumulado=resultado_acumulado
                )
                session.add(nova_posicao)
            
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
    def listar_posicoes() -> List[Posicao]:
        """
        Lista todas las posiciones con cantidad > 0
        
        Returns:
            List[Posicao]: Lista de posiciones activas
        """
        session = SessionLocal()
        try:
            return session.query(Posicao).filter(Posicao.quantidade_total > 0).all()
        finally:
            session.close()
    
    @staticmethod
    def obter_posicao_por_ativo(ativo_id: int) -> Optional[Posicao]:
        """
        Obtiene la posición de un activo específico
        
        Args:
            ativo_id: ID del activo
            
        Returns:
            Optional[Posicao]: La posición si existe, None en caso contrario
        """
        session = SessionLocal()
        try:
            return session.query(Posicao).filter(Posicao.ativo_id == ativo_id).first()
        finally:
            session.close()
    
    @staticmethod
    def atualizar_todas_posicoes() -> bool:
        """
        Actualiza todas las posiciones con precios actuales
        
        Returns:
            bool: True si todas se actualizaron correctamente
        """
        session = SessionLocal()
        try:
            # Obtener todas las posiciones
            posicoes = session.query(Posicao).all()
            
            total_atualizadas = 0
            
            for posicao in posicoes:
                try:
                    PosicaoService.atualizar_posicao(posicao.ativo_id)
                    total_atualizadas += 1
                except Exception as e:
                    logger.error(f"Erro ao atualizar posição {posicao.ativo_id}: {e}")
                    continue
            
            logger.info(f"Atualizadas {total_atualizadas} de {len(posicoes)} posições")
            return total_atualizadas == len(posicoes)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar todas as posições: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def obter_resumo_portfolio() -> dict:
        """
        Obtiene un resumen completo del portfolio
        
        Returns:
            dict: Resumen del portfolio con valores totales
        """
        session = SessionLocal()
        try:
            posicoes = session.query(Posicao).filter(Posicao.quantidade_total > 0).all()
            
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
            
            return {
                'total_ativos': total_ativos,
                'valor_total_investido': valor_total_investido,
                'valor_atual_portfolio': valor_atual_portfolio,
                'resultado_total_dia': resultado_total_dia,
                'resultado_total_acumulado': resultado_total_acumulado,
                'percentual_resultado': percentual_resultado
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo do portfolio: {e}")
            return {
                'total_ativos': 0,
                'valor_total_investido': 0,
                'valor_atual_portfolio': 0,
                'resultado_total_dia': 0,
                'resultado_total_acumulado': 0,
                'percentual_resultado': 0
            }
        finally:
            session.close()
    
    @staticmethod
    def eliminar_posicao(ativo_id: int) -> bool:
        """
        Elimina una posición (solo si cantidad = 0)
        
        Args:
            ativo_id: ID del activo
            
        Returns:
            bool: True si se eliminó correctamente
        """
        session = SessionLocal()
        try:
            posicao = session.query(Posicao).filter(Posicao.ativo_id == ativo_id).first()
            
            if not posicao:
                return True  # Ya no existe
            
            if posicao.quantidade_total > 0:
                st.error("❌ No se puede eliminar posición con cantidad > 0")
                return False
            
            session.delete(posicao)
            session.commit()
            
            logger.info(f"Posição eliminada para ativo {ativo_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao eliminar posição: {e}")
            return False
        finally:
            session.close()