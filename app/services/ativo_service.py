"""
Servicio de Activos

Este módulo contiene la lógica de negocio para la gestión de activos financieros
(agregar, eliminar, desactivar, reactivar, listar).
"""

import logging
import streamlit as st
from typing import List, Optional
from ..models import SessionLocal, Ativo
from .validacao_service import validar_ticker

# Configurar logger
logger = logging.getLogger(__name__)


class AtivoService:
    """Servicio para gestión de activos financieros"""
    
    @staticmethod
    def adicionar_ativo(ticker: str, nome: str = None) -> bool:
        """
        Añade un nuevo activo a la base de datos
        
        Args:
            ticker: Símbolo del ticker
            nome: Nombre opcional del activo
            
        Returns:
            bool: True si se agregó correctamente, False en caso contrario
        """
        session = SessionLocal()
        logger.info(f"Tentando adicionar ativo: {ticker}")
        
        try:
            ticker = ticker.upper().strip()
            
            # Verificar si ya existe
            existente = session.query(Ativo).filter(Ativo.ticker == ticker).first()
            if existente:
                logger.warning(f"Ticker {ticker} já existe na base de dados")
                st.warning(f"⚠️ El ticker {ticker} ya existe en la base de datos")
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
            
            # Crear nuevo activo
            nuevo_ativo = Ativo(
                ticker=ticker,
                nome=nome or validacao['nome'],
                ativo=True
            )
            session.add(nuevo_ativo)
            session.commit()
            
            logger.info(f"Ativo {ticker} adicionado com sucesso (fonte: {fonte})")
            st.success(f"✅ Activo {ticker} - {validacao['nome']} añadido correctamente")
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
        Lista todos los activos
        
        Args:
            apenas_ativos: Si True, solo lista activos activos
            
        Returns:
            List[Ativo]: Lista de activos
        """
        session = SessionLocal()
        try:
            query = session.query(Ativo)
            if apenas_ativos:
                query = query.filter(Ativo.ativo == True)
            return query.all()
        finally:
            session.close()
    
    @staticmethod
    def eliminar_ativo(ticker: str) -> bool:
        """
        Elimina un activo completamente de la base de datos
        
        Args:
            ticker: Símbolo del ticker a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        session = SessionLocal()
        logger.info(f"Tentando eliminar ativo: {ticker}")
        
        try:
            ticker = ticker.upper().strip()
            
            # Buscar el activo
            ativo = session.query(Ativo).filter(Ativo.ticker == ticker).first()
            if not ativo:
                st.error(f"❌ Activo {ticker} no encontrado")
                return False
            
            # Verificar si tiene posiciones con cantidades > 0
            from ..models import Posicao
            posicao = session.query(Posicao).filter(
                Posicao.ativo_id == ativo.id,
                Posicao.quantidade_total > 0
            ).first()
            
            if posicao:
                st.error(f"❌ No se puede eliminar {ticker}: tiene {posicao.quantidade_total} acciones en posición")
                logger.warning(f"Tentativa de eliminar ativo {ticker} com posição ativa: {posicao.quantidade_total}")
                return False
            
            # Eliminar cascada: operaciones, precios diarios, posiciones
            from ..models import Operacao, PrecoDiario
            
            # Contar registros antes de eliminar
            operacoes_count = session.query(Operacao).filter(Operacao.ativo_id == ativo.id).count()
            precos_count = session.query(PrecoDiario).filter(PrecoDiario.ativo_id == ativo.id).count()
            posicoes_count = session.query(Posicao).filter(Posicao.ativo_id == ativo.id).count()
            
            logger.info(f"Eliminando ativo {ticker}: {operacoes_count} operações, {precos_count} preços, {posicoes_count} posições")
            
            # Eliminar en orden correcto (dependencias primero)
            session.query(Operacao).filter(Operacao.ativo_id == ativo.id).delete()
            session.query(PrecoDiario).filter(PrecoDiario.ativo_id == ativo.id).delete()
            session.query(Posicao).filter(Posicao.ativo_id == ativo.id).delete()
            
            # Finalmente eliminar el activo
            session.delete(ativo)
            session.commit()
            
            logger.info(f"Ativo {ticker} eliminado completamente")
            st.success(f"✅ Activo {ticker} eliminado correctamente")
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
        Desactiva un activo (lo oculta pero mantiene datos)
        
        Args:
            ticker: Símbolo del ticker a desactivar
            
        Returns:
            bool: True si se desactivó correctamente, False en caso contrario
        """
        session = SessionLocal()
        logger.info(f"Tentando desativar ativo: {ticker}")
        
        try:
            ticker = ticker.upper().strip()
            
            # Buscar el activo
            ativo = session.query(Ativo).filter(Ativo.ticker == ticker).first()
            if not ativo:
                st.error(f"❌ Activo {ticker} no encontrado")
                return False
            
            if not ativo.ativo:
                st.warning(f"⚠️ El activo {ticker} ya está desactivado")
                return False
            
            # Verificar si tiene posiciones activas
            from ..models import Posicao
            posicao = session.query(Posicao).filter(
                Posicao.ativo_id == ativo.id,
                Posicao.quantidade_total > 0
            ).first()
            
            if posicao:
                st.error(f"❌ No se puede desactivar {ticker}: tiene {posicao.quantidade_total} acciones en posición")
                logger.warning(f"Tentativa de desativar ativo {ticker} com posição ativa: {posicao.quantidade_total}")
                return False
            
            # Desactivar
            ativo.ativo = False
            session.commit()
            
            logger.info(f"Ativo {ticker} desativado com sucesso")
            st.success(f"✅ Activo {ticker} desactivado correctamente")
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
        Reactiva un activo desactivado
        
        Args:
            ticker: Símbolo del ticker a reactivar
            
        Returns:
            bool: True si se reactivó correctamente, False en caso contrario
        """
        session = SessionLocal()
        logger.info(f"Tentando reativar ativo: {ticker}")
        
        try:
            ticker = ticker.upper().strip()
            
            # Buscar el activo (incluyendo desactivados)
            ativo = session.query(Ativo).filter(Ativo.ticker == ticker).first()
            if not ativo:
                st.error(f"❌ Activo {ticker} no encontrado")
                return False
            
            if ativo.ativo:
                st.warning(f"⚠️ El activo {ticker} ya está activado")
                return False
            
            # Reactivar
            ativo.ativo = True
            session.commit()
            
            logger.info(f"Ativo {ticker} reativado com sucesso")
            st.success(f"✅ Activo {ticker} reactivado correctamente")
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
        Obtiene un activo por su ticker
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Optional[Ativo]: El activo si existe, None en caso contrario
        """
        session = SessionLocal()
        try:
            ticker = ticker.upper().strip()
            return session.query(Ativo).filter(Ativo.ticker == ticker).first()
        finally:
            session.close()
    
    @staticmethod
    def obter_ativo_por_id(ativo_id: int) -> Optional[Ativo]:
        """
        Obtiene un activo por su ID
        
        Args:
            ativo_id: ID del activo
            
        Returns:
            Optional[Ativo]: El activo si existe, None en caso contrario
        """
        session = SessionLocal()
        try:
            return session.query(Ativo).filter(Ativo.id == ativo_id).first()
        finally:
            session.close()