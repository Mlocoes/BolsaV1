"""
Servicio de Activos - Multi-Usuario (FASE 3)

Este módulo contiene la lógica de negocio para la gestión de activos financieros
con soporte multi-usuario y aislamiento de datos por usuario.
"""

import logging
import streamlit as st
from typing import List, Optional
from ..models import SessionLocal, Ativo
from .validacao_service import validar_ticker
from ..utils.logging_config import get_logger
from .base_service import BaseService

# Configurar logger
logger = get_logger(__name__)


class AtivoService(BaseService):
    """Servicio para gestión de activos financieros con soporte multi-usuario"""
    
    @staticmethod
    def adicionar_ativo(ticker: str, nome: str = None) -> bool:
        """
        Añade un nuevo activo a la base de datos para el usuario actual
        
        Args:
            ticker: Símbolo del ticker
            nome: Nombre opcional del activo
            
        Returns:
            bool: True si se agregó correctamente, False en caso contrario
        """
        session = SessionLocal()
        
        try:
            # Obtener usuario actual
            user_id = AtivoService._get_current_user_id()
            ticker = ticker.upper().strip()
            
            logger.info(f"Usuario {user_id} tentando adicionar ativo: {ticker}")
            
            # Verificar si ya existe para este usuario
            existente = session.query(Ativo).filter(
                Ativo.ticker == ticker,
                Ativo.user_id == user_id
            ).first()
            
            if existente:
                logger.warning(f"Ticker {ticker} já existe para usuario {user_id}")
                st.warning(f"⚠️ El ticker {ticker} ya existe en tu cartera")
                return False
            
            # Validar que el ticker existe en Yahoo Finance
            validacao = validar_ticker(ticker)
            if not validacao['valido']:
                logger.error(f"Ticker {ticker} inválido: {validacao['erro']}")
                st.error(f"❌ {validacao['erro']}")
                return False
            
            # Mostrar warning si la validación fue manual/offline
            if 'warning' in validacao:
                st.warning(f"⚠️ {validacao['warning']}")
            
            # Mostrar info sobre la fuente de validación
            fonte = validacao.get('fonte', 'UNKNOWN')
            if fonte == 'LISTA_CONOCIDA':
                st.info(f"📋 {ticker} validado desde lista de tickers conocidos")
            elif fonte == 'MANUAL' or fonte == 'MANUAL_FALLBACK':
                st.warning(f"🔧 {ticker} agregado manualmente - validación offline")
            
            # Crear nuevo activo para el usuario
            nuevo_ativo = Ativo(
                ticker=ticker,
                nome=nome or validacao['nome'],
                ativo=True,
                user_id=user_id  # Asignar al usuario actual
            )
            session.add(nuevo_ativo)
            session.commit()
            
            logger.info(f"Usuario {user_id} adicionou ativo {ticker} com sucesso (fonte: {fonte})")
            st.success(f"✅ Activo {ticker} - {validacao['nome']} añadido correctamente a tu cartera")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao adicionar ativo {ticker}: {e}", exc_info=True)
            st.error(f"❌ Error al añadir activo: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def listar_ativos(apenas_ativos: bool = True) -> List[Ativo]:
        """
        Lista todos los activos del usuario actual
        
        Args:
            apenas_ativos: Si True, solo lista activos activos
            
        Returns:
            List[Ativo]: Lista de activos del usuario
        """
        session = SessionLocal()
        try:
            # Obtener usuario actual
            user_id = AtivoService._get_current_user_id()
            
            # Query filtrada por usuario
            query = session.query(Ativo).filter(Ativo.user_id == user_id)
            
            if apenas_ativos:
                query = query.filter(Ativo.ativo == True)
            
            ativos = query.order_by(Ativo.ticker).all()
            logger.info(f"Usuario {user_id} listou {len(ativos)} ativos")
            return ativos
            
        except Exception as e:
            logger.error(f"Erro ao listar ativos: {e}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def eliminar_ativo(ticker: str) -> bool:
        """
        Elimina un activo completamente del usuario actual
        
        Args:
            ticker: Símbolo del ticker a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        session = SessionLocal()
        
        try:
            # Obtener usuario actual
            user_id = AtivoService._get_current_user_id()
            ticker = ticker.upper().strip()
            
            logger.info(f"Usuario {user_id} tentando eliminar ativo: {ticker}")
            
            # Buscar el activo del usuario
            ativo = session.query(Ativo).filter(
                Ativo.ticker == ticker,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                st.error(f"❌ Activo {ticker} no encontrado en tu cartera")
                return False
            
            # Verificar si tiene posiciones con cantidades > 0
            from ..models import Posicao
            posicao = session.query(Posicao).filter(
                Posicao.ativo_id == ativo.id,
                Posicao.quantidade_total > 0,
                Posicao.user_id == user_id
            ).first()
            
            if posicao:
                st.error(f"❌ No se puede eliminar {ticker}: tiene {posicao.quantidade_total} acciones en posición")
                logger.warning(f"Usuario {user_id} tentou eliminar ativo {ticker} com posição ativa: {posicao.quantidade_total}")
                return False
            
            # Eliminar cascada: operaciones, precios diarios, posiciones del usuario
            from ..models import Operacao, PrecoDiario
            
            # Contar registros antes de eliminar (solo del usuario)
            operacoes_count = session.query(Operacao).filter(
                Operacao.ativo_id == ativo.id,
                Operacao.user_id == user_id
            ).count()
            
            precos_count = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo.id,
                PrecoDiario.user_id == user_id
            ).count()
            
            posicoes_count = session.query(Posicao).filter(
                Posicao.ativo_id == ativo.id,
                Posicao.user_id == user_id
            ).count()
            
            logger.info(f"Usuario {user_id} eliminando ativo {ticker}: {operacoes_count} operações, {precos_count} preços, {posicoes_count} posições")
            
            # Eliminar en orden correcto (dependencias primero) - solo del usuario
            session.query(Operacao).filter(
                Operacao.ativo_id == ativo.id,
                Operacao.user_id == user_id
            ).delete()
            
            session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo.id,
                PrecoDiario.user_id == user_id
            ).delete()
            
            session.query(Posicao).filter(
                Posicao.ativo_id == ativo.id,
                Posicao.user_id == user_id
            ).delete()
            
            # Finalmente eliminar el activo del usuario
            session.delete(ativo)
            session.commit()
            
            logger.info(f"Usuario {user_id} eliminó ativo {ticker} completamente")
            st.success(f"✅ Activo {ticker} eliminado correctamente de tu cartera")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao eliminar ativo {ticker}: {e}", exc_info=True)
            st.error(f"❌ Error al eliminar activo: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def desactivar_ativo(ticker: str) -> bool:
        """
        Desactiva un activo del usuario actual (lo oculta pero mantiene datos)
        
        Args:
            ticker: Símbolo del ticker a desactivar
            
        Returns:
            bool: True si se desactivó correctamente, False en caso contrario
        """
        session = SessionLocal()
        
        try:
            # Obtener usuario actual
            user_id = AtivoService._get_current_user_id()
            ticker = ticker.upper().strip()
            
            logger.info(f"Usuario {user_id} tentando desativar ativo: {ticker}")
            
            # Buscar el activo del usuario
            ativo = session.query(Ativo).filter(
                Ativo.ticker == ticker,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                st.error(f"❌ Activo {ticker} no encontrado en tu cartera")
                return False
            
            if not ativo.ativo:
                st.warning(f"⚠️ El activo {ticker} ya está desactivado")
                return False
            
            # Verificar si tiene posiciones activas
            from ..models import Posicao
            posicao = session.query(Posicao).filter(
                Posicao.ativo_id == ativo.id,
                Posicao.quantidade_total > 0,
                Posicao.user_id == user_id
            ).first()
            
            if posicao:
                st.error(f"❌ No se puede desactivar {ticker}: tiene {posicao.quantidade_total} acciones en posición")
                logger.warning(f"Usuario {user_id} tentou desativar ativo {ticker} com posição ativa: {posicao.quantidade_total}")
                return False
            
            # Desactivar
            ativo.ativo = False
            session.commit()
            
            logger.info(f"Usuario {user_id} desativou ativo {ticker} com sucesso")
            st.success(f"✅ Activo {ticker} desactivado correctamente en tu cartera")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao desativar ativo {ticker}: {e}", exc_info=True)
            st.error(f"❌ Error al desactivar activo: {e}")
            return False
        finally:
            session.close()
    @staticmethod
    def reactivar_ativo(ticker: str) -> bool:
        """
        Reactiva un activo desactivado del usuario actual
        
        Args:
            ticker: Símbolo del ticker a reactivar
            
        Returns:
            bool: True si se reactivó correctamente, False en caso contrario
        """
        session = SessionLocal()
        
        try:
            # Obtener usuario actual
            user_id = AtivoService._get_current_user_id()
            ticker = ticker.upper().strip()
            
            logger.info(f"Usuario {user_id} tentando reativar ativo: {ticker}")
            
            # Buscar el activo del usuario (incluyendo desactivados)
            ativo = session.query(Ativo).filter(
                Ativo.ticker == ticker,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                st.error(f"❌ Activo {ticker} no encontrado en tu cartera")
                return False
            
            if ativo.ativo:
                st.warning(f"⚠️ El activo {ticker} ya está activado")
                return False
            
            # Reactivar
            ativo.ativo = True
            session.commit()
            
            logger.info(f"Usuario {user_id} reativou ativo {ticker} com sucesso")
            st.success(f"✅ Activo {ticker} reactivado correctamente en tu cartera")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao reativar ativo {ticker}: {e}", exc_info=True)
            st.error(f"❌ Error al reactivar activo: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def obter_ativo_por_ticker(ticker: str) -> Optional[Ativo]:
        """
        Obtiene un activo por su ticker del usuario actual
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Optional[Ativo]: El activo si existe en la cartera del usuario, None en caso contrario
        """
        session = SessionLocal()
        try:
            user_id = AtivoService._get_current_user_id()
            ticker = ticker.upper().strip()
            
            return session.query(Ativo).filter(
                Ativo.ticker == ticker,
                Ativo.user_id == user_id
            ).first()
            
        except Exception as e:
            logger.error(f"Erro ao obter ativo por ticker {ticker}: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def obter_ativo_por_id(ativo_id: int) -> Optional[Ativo]:
        """
        Obtiene un activo por su ID, verificando que pertenezca al usuario actual
        
        Args:
            ativo_id: ID del activo
            
        Returns:
            Optional[Ativo]: El activo si existe y pertenece al usuario, None en caso contrario
        """
        session = SessionLocal()
        try:
            user_id = AtivoService._get_current_user_id()
            
            return session.query(Ativo).filter(
                Ativo.id == ativo_id,
                Ativo.user_id == user_id
            ).first()
            
        except Exception as e:
            logger.error(f"Erro ao obter ativo por ID {ativo_id}: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def get_ativos_count(user_id: int = None) -> int:
        """
        Obtiene el número total de activos de un usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            int: Número de activos del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = AtivoService._get_current_user_id()
            
            return session.query(Ativo).filter(
                Ativo.user_id == user_id,
                Ativo.ativo == True
            ).count()
            
        except Exception as e:
            logger.error(f"Erro ao contar ativos do usuario {user_id}: {e}")
            return 0
        finally:
            session.close()
    
    @staticmethod
    def get_user_statistics(user_id: int = None) -> dict:
        """
        Obtiene estadísticas de activos de un usuario
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            dict: Estadísticas del usuario
        """
        session = SessionLocal()
        try:
            if user_id is None:
                user_id = AtivoService._get_current_user_id()
            
            total_ativos = session.query(Ativo).filter(
                Ativo.user_id == user_id
            ).count()
            
            ativos_ativos = session.query(Ativo).filter(
                Ativo.user_id == user_id,
                Ativo.ativo == True
            ).count()
            
            ativos_inativos = total_ativos - ativos_ativos
            
            return {
                'total_ativos': total_ativos,
                'ativos_ativos': ativos_ativos,
                'ativos_inativos': ativos_inativos,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do usuario {user_id}: {e}")
            return {
                'total_ativos': 0,
                'ativos_ativos': 0,
                'ativos_inativos': 0,
                'user_id': user_id
            }
        finally:
            session.close()